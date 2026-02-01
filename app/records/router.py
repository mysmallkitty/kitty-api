from fastapi import APIRouter
from app.records.schemas import UserLeaderboardSchema
from app.user.models import User
from app.records.redis_services import global_stats_service, ccu_service

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)


# 전체 유저 리더보드 (PP순)
@router.get("/leaderboard", response_model=list[UserLeaderboardSchema])
async def get_global_leaderboard(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    return await User.all().order_by("-total_pp").offset(offset).limit(limit)


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