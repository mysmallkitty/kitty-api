
from fastapi import APIRouter, WebSocket
from app.play.websocket import websocket_game_handler


router = APIRouter(
    prefix="/api/v1",
    tags=["play"],
    responses={404: {"description": "Not found"}},
)


@router.websocket("/{map_id}/play")
async def play_map(
    websocket: WebSocket,
    map_id: int,
    token: str
):
    """
    게임 플레이 WebSocket 엔드포인트
    
    클라이언트 → 서버 메시지:
    - {"type": "position", "pos": {"x": 100, "y": 200}}  # 100ms마다
    - {"type": "death"}  # 죽을 때마다
    - {"type": "clear"}  # 클리어 시
    
    서버 → 클라이언트 메시지:
    - {"type": "session_started", "session_id": "...", "map_id": 1}
    - {"type": "death_ack", "total_deaths": 5}
    - {"type": "clear_success", "clear_time": 45230, "deaths": 15}
    - {"type": "error", "message": "..."}
    """
    await websocket_game_handler(websocket, map_id, token)