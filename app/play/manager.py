import time
import logging
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket
from pydantic import ValidationError
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.play.schemas import (
    DeathAck,
    PositionMessage,
    DeathMessage,
    ClearMessage,
    ChatMessage,
    GhostPositionMessage,
    ChatBroadcast,
    ClearAck,
)
from app.records.models import Record, Stat
from app.records.pp.calculate_pp import calculate_pp
from app.records.redis_services import ranking_service
from app.maps.models import Map
from app.user.models import User

logger = logging.getLogger(__name__)


class GameSession:
    def __init__(self, map_id: int, user_id: int):
        self.map_id = map_id
        self.user_id = user_id
        self.deaths = 0
        self.last_dir: float | None = None
        self.start_time = time.time()
        self.clear_time = None
        self.is_cleared = False


POSITION_THROTTLE = 0.01


class GameWebSocketManager:
    def __init__(self):
        self.handlers = {}
        self.active_sessions: Dict[str, GameSession] = {}
        self.last_position_time: Dict[str, float] = defaultdict(float)
        self.active_websockets: Dict[str, WebSocket] = {}
        self.map_sessions: Dict[int, Set[str]] = defaultdict(set)

    def handler(self, message_type: str):
        def decorator(func):
            self.handlers[message_type] = func
            return func

        return decorator

    async def dispatch(self, websocket: WebSocket, session_id: str, data: dict):
        message_type = data.get("type")
        handler = self.handlers.get(message_type)
        if not handler:
            logger.warning(f"Unknown message type: {message_type}")
            return
        await handler(websocket, session_id, data)

    async def connect(self, websocket: WebSocket, session_id: str, map_id: int, user_id: int):
        self.active_sessions[session_id] = GameSession(map_id, user_id)
        self.active_websockets[session_id] = websocket
        self.map_sessions[map_id].add(session_id)
        await self.broadcast(session_id, {"type": "peer_joined", "user_id": user_id})

    async def disconnect(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            return
        await self.broadcast(session_id, {"type": "peer_left", "user_id": session.user_id})
        map_id = session.map_id
        if map_id in self.map_sessions:
            self.map_sessions[map_id].discard(session_id)
            if not self.map_sessions[map_id]:
                del self.map_sessions[map_id]
        self.active_sessions.pop(session_id, None)
        self.active_websockets.pop(session_id, None)
        self.last_position_time.pop(session_id, None)

    async def broadcast(self, session_id: str, message: dict):
        session = self.get_session(session_id)
        if not session or session.map_id not in self.map_sessions:
            return
        for other_session_id in list(self.map_sessions[session.map_id]):
            if other_session_id == session_id:
                continue
            ws = self.active_websockets.get(other_session_id)
            if not ws:
                continue
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Broadcast failed: {other_session_id}, {e}")
                await self.disconnect(other_session_id)

    def get_session(self, session_id: str) -> GameSession | None:
        return self.active_sessions.get(session_id)


manager = GameWebSocketManager()


@manager.handler("position")
async def handle_position(websocket: WebSocket, session_id: str, data: dict):
    try:
        PositionMessage.model_validate(data)
    except ValidationError:
        return

    current_time = time.time()
    if current_time - manager.last_position_time[session_id] < POSITION_THROTTLE:
        return
    manager.last_position_time[session_id] = current_time

    session = manager.get_session(session_id)
    if session:
        pos = data.get("pos", {})
        session.last_dir = pos.get("dir")
        ghost_message = GhostPositionMessage(user_id=session.user_id, pos=pos)
        await manager.broadcast(session_id, ghost_message.model_dump())


@manager.handler("death")
async def handle_death(websocket: WebSocket, session_id: str, data: dict):
    try:
        DeathMessage.model_validate(data)
    except ValidationError:
        return

    session = manager.get_session(session_id)
    if not session:
        return
    session.deaths += 1
    if data.get("dir") is not None:
        session.last_dir = data.get("dir")
    await websocket.send_json(DeathAck(total_deaths=session.deaths).model_dump())
    await manager.broadcast(session_id, {"type": "death", "player_id": session.user_id, "dir": session.last_dir})


@manager.handler("chat")
async def handle_chat(websocket: WebSocket, session_id: str, data: dict):
    try:
        ChatMessage.model_validate(data)
    except ValidationError:
        return
    session = manager.get_session(session_id)
    if not session:
        return
    text = str(data.get("text", "")).strip()
    if text == "":
        return
    text = text[:200]
    broadcast = ChatBroadcast(user_id=session.user_id, text=text)
    await manager.broadcast(session_id, broadcast.model_dump())


async def _recompute_total_pp(user_id: int) -> float:
    records = (
        await Record.filter(user_id=user_id, pp__not_isnull=True)
        .order_by("-pp")
        .limit(100)
    )
    total = 0.0
    weight = 1.0
    decay = 0.95
    for r in records:
        if r.pp is None:
            continue
        total += float(r.pp) * weight
        weight *= decay
    return total


@manager.handler("clear")
async def handle_clear(websocket: WebSocket, session_id: str, data: dict):
    try:
        ClearMessage.model_validate(data)
    except ValidationError:
        return

    session = manager.get_session(session_id)
    if not session or session.is_cleared:
        return

    clear_time = int(data.get("clear_time", 0))
    # Use client-reported deaths for the record (checkpoint resets),
    # but keep server-side deaths for aggregate stats.
    record_deaths = int(data.get("deaths", 0))
    stats_deaths = int(session.deaths or 0)
    session.clear_time = clear_time
    session.is_cleared = True

    map_obj = await Map.get(id=session.map_id)

    class TempRecord:
        def __init__(self, deaths, clear_time):
            self.deaths = deaths
            self.clear_time = clear_time

    current_pp = 0.0
    if map_obj.is_ranked:
        current_pp = float(calculate_pp(map_obj, TempRecord(record_deaths, clear_time)))

    async with in_transaction():
        stat, _ = await Stat.get_or_create(user_id=session.user_id, map_id=session.map_id)
        stat.deaths += stats_deaths
        stat.is_cleared = True
        await stat.save()

        await Map.filter(id=session.map_id).update(
            total_deaths=F("total_deaths") + stats_deaths,
            total_clears=F("total_clears") + 1,
        )
        await User.filter(id=session.user_id).update(
            total_deaths=F("total_deaths") + stats_deaths,
            total_clears=F("total_clears") + 1,
        )

        best_record = await Record.filter(user_id=session.user_id, map_id=session.map_id).first()
        old_pp = best_record.pp if best_record and best_record.pp else 0

        # 항상 기록은 남기고, 랭크드 맵이면 PP 향상 시 랭킹 갱신
        if best_record is None:
            await Record.create(
                user_id=session.user_id,
                map_id=session.map_id,
                pp=current_pp,
                clear_time=clear_time,
                deaths=record_deaths,
                replay_url="",
            )
        elif current_pp > old_pp:
            best_record.pp = current_pp
            best_record.clear_time = clear_time
            best_record.deaths = record_deaths
            await best_record.save()

        if current_pp > old_pp:
            new_total_pp = await _recompute_total_pp(session.user_id)
            await User.filter(id=session.user_id).update(total_pp=new_total_pp)
            await ranking_service.update_user_pp(session.user_id, new_total_pp)

    rank = await ranking_service.get_rank(session.user_id)
    await websocket.send_json(
    ClearAck(clear_time=clear_time, deaths=record_deaths, pp=current_pp, rank=rank or 0).model_dump()
    )
