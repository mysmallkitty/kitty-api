import time
import logging
from collections import defaultdict
from typing import Dict, Set

from fastapi import HTTPException, WebSocket
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
from app.records.services import pp_service, clear_service
from app.play.service import check_and_finish_game, room_service
from app.records.redis_services import ranking_service
from app.maps.models import Map
from app.user.models import User

logger = logging.getLogger(__name__)


class GameSession:
    def __init__(self, map_id: int, user_id: int, username:str, room_id: str | None = None):
        self.map_id = map_id
        self.user_id = user_id
        self.username = username
        self.room_id = room_id
        self.deaths = 0
        self.last_dir: float | None = None
        self.start_time = time.time()
        self.clear_time = None
        self.is_cleared = False
        self.place = None
        self.started = False


POSITION_THROTTLE = 0.01


class GameWebSocketManager:
    def __init__(self):
        self.handlers = {}
        self.active_sessions: Dict[str, GameSession] = {}
        self.last_position_time: Dict[str, float] = defaultdict(float)
        self.active_websockets: Dict[str, WebSocket] = {}
        self.game_groups: Dict[tuple, Set[str]] = defaultdict(set)

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

    async def connect(self, websocket: WebSocket, session_id: str, map_id: int, user_id: int, username: str, room_id: str | None = None):
        self.active_sessions[session_id] = GameSession(map_id, user_id, username, room_id)
        self.active_websockets[session_id] = websocket
        
        group_key = (map_id, room_id)
        self.game_groups[group_key].add(session_id)
        await self.broadcast_to_group(
            group_key=group_key, 
            message={
                "type": "peer_joined", 
                "user_id": user_id,
                "username": username,
                "message": f"{username} joined the game!"
            }, 
            exclude_session=session_id
        )

    async def disconnect(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            return

        room_id = session.room_id
        user_id = session.user_id
        username = session.username
        map_id = session.map_id

        group_key = (map_id, room_id)
        
        if room_id:
            try:
                await room_service.leave_room(room_id, user_id)
            except HTTPException:
                pass
            
            await self.broadcast_to_group(group_key, {
                "type": "player_left",
                "user_id": user_id,
                "username": username,
                "message": f"{username} left the game!"
            }, exclude_session=session_id)

        self.game_groups[group_key].discard(session_id)
        
        if not self.game_groups[group_key]:
            del self.game_groups[group_key]
        
        self.active_sessions.pop(session_id, None)
        self.active_websockets.pop(session_id, None)
        self.last_position_time.pop(session_id, None)

    async def broadcast(self, session_id: str, message: dict):
        session = self.get_session(session_id)
        if not session:
            return
        group_key = (session.map_id, session.room_id)
        
        for other_session_id in list(self.game_groups[group_key]):
            if other_session_id == session_id:
                continue
            ws = self.active_websockets.get(other_session_id)
            if ws:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.warning(f"Broadcast failed: {other_session_id}, {e}")
                    await self.disconnect(other_session_id)

    async def broadcast_to_group(self, group_key: tuple, message: dict, exclude_session: str | None = None):
        for sid in list(self.game_groups.get(group_key, [])):
            if sid == exclude_session:
                continue
                
            ws = self.active_websockets.get(sid)
            if ws:
                try:
                    await ws.send_json(message)
                except Exception:
                    await self.disconnect(sid)

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
    if not session.started:
        return
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



@manager.handler("clear")
async def handle_clear(websocket: WebSocket, session_id: str, data: dict):
    try:
        ClearMessage.model_validate(data)
    except ValidationError:
        return

    session = manager.get_session(session_id)
    if not session or session.is_cleared:
        return
    
    rank_before = await ranking_service.get_rank(session.user_id)

    old_record = await Record.get_or_none(user_id=session.user_id, map_id=session.map_id)
    old_best_time = old_record.clear_time if old_record else None

    clear_time = int(data.get("clear_time", 0))
    record_deaths = int(data.get("deaths", 0))
    session.clear_time = clear_time
    session.is_cleared = True

    if session.room_id:
        group_key = (session.map_id, session.room_id)
        cleared_sessions = []
    
        for sid in manager.game_groups.get(group_key, []):
            s = manager.get_session(sid)
            if s and s.is_cleared and s.clear_time is not None:
                cleared_sessions.append(s)

        cleared_sessions.sort(key=lambda x: x.clear_time)
        
        for place, s in enumerate(cleared_sessions, start=1):
            s.place = place

    map_obj = await Map.get(id=session.map_id)
    current_pp = pp_service.calculate_pp_for_clear(map_obj, record_deaths, clear_time)

    async with in_transaction():
        stat, created = await Stat.get_or_create(user_id=session.user_id, map_id=session.map_id)
        if not stat.is_cleared:
            stat.is_cleared = True
            await clear_service.increment_global_clears(session.user_id, session.map_id)
        await stat.save()

        await pp_service.update_record_and_ranking(
            user_id=session.user_id,
            map_id=session.map_id,
            clear_time=clear_time,
            deaths=record_deaths,
            current_pp=current_pp
        )

    rank_after = await ranking_service.get_rank(session.user_id)

    rank_diff = (rank_before - rank_after) if (rank_before is not None and rank_after is not None) else 0
    time_diff = (old_best_time - clear_time) if old_best_time is not None else None

    if session.room_id:
        await manager.broadcast(session_id, {
            "type": "player_finished",
            "user_id": session.user_id,
            "username": session.username,
            "place": session.place,
            "clear_time": clear_time,
            "deaths": record_deaths
        })
    
    await websocket.send_json(
        ClearAck(
            clear_time=clear_time,
            deaths=record_deaths,
            pp=current_pp,
            rank=rank_after or 0,
            rank_diff=rank_diff,
            time_diff=time_diff
        ).model_dump()
    )
    if session.room_id:
        await check_and_finish_game(session_id)

@manager.handler("update_ready")
async def handle_ready(websocket: WebSocket, session_id: str, data: dict):
    session = manager.get_session(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": "Invalid session"})
        return
    
    if not session.room_id:
        await websocket.send_json({"type": "error", "message": "Not in a room"})
        return
    is_ready = data.get("is_ready", False)
    try:
        await room_service.update_ready_status(session.room_id, session.user_id, is_ready)
        await manager.broadcast(session_id, {
            "type": "ready_status_changed",
            "user_id": session.user_id,
            "username": session.username,
            "is_ready": is_ready
        })
        await websocket.send_json({
            "type": "ready_success", 
            "is_ready": is_ready
        })
    except HTTPException as e:
        await websocket.send_json({"type": "error", "message": e.detail})

@manager.handler("kick_player")
async def handle_kick(websocket: WebSocket, session_id: str, data: dict):
    session = manager.get_session(session_id)
    target_user_id = data.get("target_id")
    
    if not session or not session.room_id or not target_user_id:
        return

    try:
        await room_service.kick_player(session.room_id, session.user_id, target_user_id)
        
        await manager.broadcast(session_id, {
            "type": "player_kicked",
            "target_id": target_user_id
        })
        
        for sid, s_obj in list(manager.active_sessions.items()):
            if s_obj.user_id == target_user_id and s_obj.room_id == session.room_id:
                target_ws = manager.active_websockets.get(sid)
                if target_ws:
                    await target_ws.send_json({"type": "kicked_by_host"})
                    await target_ws.close(code=1000)
                break
                
    except HTTPException as e:
        await websocket.send_json({"type": "error", "message": e.detail})
    except Exception:
        await websocket.send_json({"type": "error", "message": "error while kicking player"})

@manager.handler("start_game")
async def handle_start(websocket: WebSocket, session_id: str, data: dict):
    session = manager.get_session(session_id)
    if not session: return

    target_sessions = []
    if session.room_id:
        try:
            await room_service.start_game(session.room_id, session.user_id)
            group_key = (session.map_id, session.room_id)
            target_sessions = [manager.get_session(sid) for sid in manager.game_groups.get(group_key, [])]
        except HTTPException as e:
            await websocket.send_json({"type": "error", "message": e.detail})
            return
    else:
        target_sessions = [session]

    try:
        async with in_transaction():
            for s in target_sessions:
                if not s: continue
                s.started = True 
                
                stat, _ = await Stat.get_or_create(user_id=s.user_id, map_id=s.map_id)
                stat.attempts += 1
                await stat.save()

                await User.filter(id=s.user_id).update(total_attempts=F("total_attempts") + 1)
            
            await Map.filter(id=session.map_id).update(total_attempts=F("total_attempts") + len(target_sessions))

        if session.room_id:
            await manager.broadcast(session_id, {
                "type": "game_start",
                "map_id": session.map_id,
                "room_id": session.room_id
            })
        
        await websocket.send_json({"type": "game_start_success"})

    except Exception as e:
        await websocket.send_json({"type": "error", "message": "server status update error"})