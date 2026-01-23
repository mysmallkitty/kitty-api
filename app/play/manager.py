
from collections import defaultdict
import logging
import time
from typing import Dict
from fastapi import WebSocket
from pydantic import ValidationError

from app.play.schemas import (
    DeathAck,
    ClearSuccess,
    PositionMessage,
    DeathMessage,
    ClearMessage,
)

# 로거 설정
logger = logging.getLogger(__name__)

class GameSession:
    """게임 세션 데이터"""
    def __init__(self, map_id: int, user_id: int):
        self.map_id = map_id
        self.user_id = user_id
        self.deaths = 0
        self.start_time = time.time()
        self.clear_time = None
        self.is_cleared = False
        
# 설정
POSITION_THROTTLE = 0.1  # 100ms - 초당 10회

class GameWebSocketManager:
    def __init__(self):
        self.handlers = {}
        self.active_sessions: Dict[str, GameSession] = {}
        self.last_position_time: Dict[str, float] = defaultdict(float)

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

    def connect(self, session_id: str, map_id: int, user_id: int):
        self.active_sessions[session_id] = GameSession(map_id, user_id)

    # 세션 종료하면 리소스 정리
    def disconnect(self, session_id: str):
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.last_position_time:
            del self.last_position_time[session_id]

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
    await websocket.send_json(DeathAck(total_deaths=session.deaths).model_dump())


@manager.handler("clear")
async def handle_clear(websocket: WebSocket, session_id: str, data: dict):
    try:
        ClearMessage.model_validate(data)
    except ValidationError:
        return

    session = manager.get_session(session_id)
    if not session:
        return
    current_time = time.time()
    session.is_cleared = True
    session.clear_time = int((current_time - session.start_time) * 1000)
    await websocket.send_json(
        ClearSuccess(
            clear_time=session.clear_time, deaths=session.deaths
        ).model_dump()
    )
