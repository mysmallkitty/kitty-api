import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tortoise.expressions import F
from tortoise.transactions import in_transaction
from app.maps.models import Map
from app.play.manager import manager
from app.play.schemas import ClearSuccess, GameClearRequest
from app.play.websocket import verify_websocket_token, websocket_game_handler
from app.records.models import Record, Stat
from app.records.pp.calculate_pp import calculate_pp
from app.records.pp.total_pp import recompute_total_pp
from app.records.redis_services import ranking_service
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



@router.post("/clear", response_model=ClearSuccess)
async def clear(request: GameClearRequest, user=Depends(get_current_user)):
    session = manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    if session.is_cleared:
        raise HTTPException(status_code=400, detail="Already cleared")

    current_time = time.time()
    clear_time = int((current_time - session.start_time) * 1000)
    session.is_cleared = True
    session.clear_time = clear_time

    map_obj = await Map.get(id=session.map_id)

    class TempRecord:
        def __init__(self, deaths, clear_time):
            self.deaths = deaths
            self.clear_time = clear_time


    current_pp = 0.0
    if map_obj.is_ranked:
        current_pp = float(calculate_pp(map_obj, TempRecord(session.deaths, clear_time)))

    async with in_transaction():
        stat, _ = await Stat.get_or_create(user_id=session.user_id, map_id=session.map_id)
        if not stat.is_cleared:
            stat.is_cleared = True
            await stat.save()
            await User.filter(id=session.user_id).update(total_clears=F("total_clears") + 1)
            await Map.filter(id=session.map_id).update(total_clears=F("total_clears") + 1)

        best_record = await Record.filter(user_id=session.user_id, map_id=session.map_id).first()
        old_pp = best_record.pp if best_record and best_record.pp else 0

        if current_pp > old_pp:
            if best_record:
                best_record.pp = current_pp
                best_record.clear_time = clear_time
                best_record.deaths = session.deaths
                await best_record.save()
            else:
                await Record.create(
                    user_id=user.id, map_id=session.map_id,
                    pp=current_pp, clear_time=clear_time, deaths=session.deaths, replay_url=""
                )

            new_total_pp = await recompute_total_pp(user.id)
            await User.filter(id=user.id).update(total_pp=new_total_pp)
            await ranking_service.update_user_pp(user.id, new_total_pp)

    # 결과 반환
    rank = await ranking_service.get_rank(user.id)

    return ClearSuccess(
        clear_time=clear_time,
        deaths=session.deaths,
        pp=current_pp,
        rank=rank if rank else 0,
    )


@router.websocket("/{map_id}/play")
async def play_map(websocket: WebSocket, map_id: int, token: str):
    """
    게임 플레이 WebSocket 엔드포인트
    - {"type": "position", "pos": {"x": 100, "y": 200}}  # 100ms마다
    - {"type": "death"}

    - {"type": "session_started", "session_id": "...", "map_id": 1}
    - {"type": "death_ack", "total_deaths": 5}
    - {"type": "error", "message": "..."}
    """
    await websocket_game_handler(websocket, map_id, token)
