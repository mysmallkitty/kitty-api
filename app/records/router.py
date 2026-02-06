import asyncio
from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Request
from sse_starlette import EventSourceResponse
from app.maps.router import get_optional_user
from app.play.router import get_current_user
from app.records.schemas import UserLeaderboardSchema
from app.user.models import User
from app.records.redis_services import global_stats_service, ccu_service, ranking_service

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)


# 전체 유저 리더보드 (PP순)
@router.get("/leaderboard", response_model=list[UserLeaderboardSchema])
async def get_global_leaderboard(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    entries = await ranking_service.get_leaderboard_page(offset, limit)
    if not entries:
        return []
    user_ids = [int(user_id) for user_id, _ in entries]
    users = await User.filter(id__in=user_ids).only(
        "id",
        "username",
        "profile_sprite",
        "country",
        "total_pp",
        "total_clears",
    )
    user_map = {user.id: user for user in users}
    ordered = []
    for i, (user_id, _score) in enumerate(entries, start=offset + 1):
        user = user_map.get(int(user_id))
        if not user:
            continue
        user.rank = i
        ordered.append(user)
    return ordered


# 24시간 죽음 횟수 반환
@router.get("/global-deaths")
async def get_today_cat_deaths():
    count = await global_stats_service.get_recent_deaths()
    return {
        "recent_24h_deaths": count,
    }

# 동시 접속자 반환
@router.get("/ccu")
async def get_ccu():
    return await ccu_service.get_ccu()

# 유저 접속
@router.get("/presence/stream")
async def presence_stream(
    request: Request, 
    current_user: Optional[User] = Depends(get_optional_user) 
):
    if current_user:
        presence_id = f"user:{current_user.id}"
    else:
        presence_id = f"guest:{uuid.uuid4()}"

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                await ccu_service.ping(presence_id)
                yield {"event": "ping", "data": "staying_alive"}
                await asyncio.sleep(15)

        except asyncio.CancelledError:
            pass

        finally:
            if current_user:
                await User.filter(id=current_user.id).update(last_login_at=datetime.now())
                print(f"User {current_user.id} logged out. DB updated.")
            else:
                print(f"Guest {presence_id} disconnected.")

    return EventSourceResponse(event_generator())


@router.post("/presence/ping")
async def presence_ping(current_user: Optional[User] = Depends(get_optional_user)):
    if current_user:
        await ccu_service.ping(f"user:{current_user.id}")
        return {"ok": True}
    return {"ok": False}
