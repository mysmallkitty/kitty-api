
import time
from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket
from tortoise.expressions import F
from tortoise.transactions import in_transaction
from app.maps.models import Map
from app.play.manager import manager
from app.play.schemas import ClearSuccess, GameClearRequest
from app.play.websocket import verify_websocket_token, websocket_game_handler
from app.records.models import Record, Stat


router = APIRouter(
    prefix="/api/v1",
    tags=["play"],
    responses={404: {"description": "Not found"}},
)


async def get_current_user(authorization: Annotated[str, Header()]):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return await verify_websocket_token(token)
    except ValueError:
         raise HTTPException(status_code=401, detail="Invalid authorization header")


@router.post("/clear", response_model=ClearSuccess)
async def clear(request: GameClearRequest, user=Depends(get_current_user)):
    """게임 클리어 API"""
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
    
    async with in_transaction():
        stat, _ = await Stat.get_or_create(user_id=user.id, map_id=session.map_id)
        if not stat.is_cleared:
            stat.is_cleared = True
            await stat.save()
        
        best_record = await Record.filter(
            user_id=user.id,
            map_id=session.map_id
        ).order_by("clear_time").first()
        
        if not best_record or (best_record.clear_time is None) or clear_time < best_record.clear_time:
            if best_record:
                best_record.clear_time = clear_time
                best_record.deaths = session.deaths
                await best_record.save()
            else:
                await Record.create(
                    user_id=user.id, map_id=session.map_id, deaths=session.deaths, clear_time=clear_time, replay_url=""
                )
                await Map.filter(id=session.map_id).update(total_clears=F("total_clears") + 1)

    return ClearSuccess(clear_time=clear_time, deaths=session.deaths)

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
    
    서버 → 클라이언트 메시지:
    - {"type": "session_started", "session_id": "...", "map_id": 1}
    - {"type": "death_ack", "total_deaths": 5}
    - {"type": "error", "message": "..."}
    """
    await websocket_game_handler(websocket, map_id, token)