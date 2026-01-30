from typing import Literal, Optional
from pydantic import BaseModel


class WebSocketResponse(BaseModel):
    type: str


class SessionStarted(WebSocketResponse):
    type: Literal["session_started"] = "session_started"
    session_id: str
    map_id: int


class DeathAck(WebSocketResponse):
    type: Literal["death_ack"] = "death_ack"
    total_deaths: int


class ClearSuccess(WebSocketResponse):
    type: Literal["clear_success"] = "clear_success"
    clear_time: int
    deaths: int
    pp: float
    rank: int


class ErrorResponse(WebSocketResponse):
    type: Literal["error"] = "error"
    message: str


# --- Incoming Messages (Client -> Server) ---
# 필요 시 핸들러에서 데이터 검증용으로 사용
class PositionData(BaseModel):
    x: float
    y: float


class PositionMessage(BaseModel):
    type: Literal["position"]
    pos: PositionData


class DeathMessage(BaseModel):
    type: Literal["death"]


class GhostPositionMessage(BaseModel):
    type: Literal["ghost_position"] = "ghost_position"
    user_id: int
    pos: PositionData


class GameClearRequest(BaseModel):
    session_id: str

class UserEndSessionMessage(BaseModel):
    type: str = "UserEndSession"
    user_id: int