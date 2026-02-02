from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.play.websocket import verify_websocket_token, websocket_game_handler


router = APIRouter(
    prefix="/api/v1",
    tags=["play"],
    responses={404: {"description": "Not found"}},
)


security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return await verify_websocket_token(credentials.credentials)


@router.websocket("/{map_id}/play")
async def play_map(websocket: WebSocket, map_id: int, token: str):
    """
    게임 플레이 WebSocket 엔드포인트

    클라이언트 → 서버 메시지 (보내는 것):
    - {"type": "position", "pos": {"x": 100, "y": 200}}  # 10ms~100ms 간격 권장
    - {"type": "death"}  # 고양이가 죽었을 때

    서버 → 클라이언트 메시지 (받는 것):
    - {"type": "session_started", "session_id": "...", "map_id": 1}  # 연결 성공 시
    - {"type": "death_ack", "total_deaths": 5}  # 죽음 기록 확인
    - {"type": "ghost_position", "user_id": 1, "pos": {"x": 100, "y": 200}}  # 타 유저 이동
    - {"type": "UserEndSession", "user_id": 1}  # 타 유저 퇴장 (고스트 제거용)
    - {"type": "error", "message": "..."}  # 오류 발생 시
    """
    await websocket_game_handler(websocket, map_id, token)
