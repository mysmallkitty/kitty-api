import time
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tortoise.expressions import F
from tortoise.transactions import in_transaction
from app.maps.models import Map
from app.play.manager import manager
from app.play.schemas import ClearSuccess, GameClearRequest
from app.play.websocket import verify_websocket_token, websocket_game_handler
from app.records.models import Record, Stat
from app.records.pp.calculate_pp import calculate_pp
from app.records.redis_services import ranking_service
from app.records.services import clear_service, result_service
from app.user.models import User


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

# 게임 클리어
@router.post("/clear", response_model=ClearSuccess)
async def clear(request: GameClearRequest, user=Depends(get_current_user)):
    session = manager.get_session(request.session_id)
    if not session: raise HTTPException(404, "Session not found")

    rank_before = await ranking_service.get_rank(user.id) or 0

    clear_time = int((time.time() - session.start_time) * 1000)
    session.is_cleared = True

    # 2. Record 생성
    record = await Record.create(
        user_id=user.id, map_id=session.map_id,
        clear_time=clear_time, deaths=session.deaths,
        pp=0, replay_url=""
    )

    # clear + 1
    await clear_service.mark_first_clear(user.id, session.map_id)
    # pp 계산, 레디스
    await result_service.process_record(record.id)

    # 랭크 차이 계산
    rank_after = await ranking_service.get_rank(user.id) or rank_before
    rank_diff = rank_before - rank_after if rank_before > 0 else 0

    await record.refresh_from_db()

    return ClearSuccess(
        record_id=record.id,
        clear_time=clear_time,
        deaths=session.deaths,
        pp=record.pp,
        rank=rank_after,
        rank_diff=max(0, rank_diff),
    )

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
