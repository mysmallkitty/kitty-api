from fastapi import APIRouter
from app.records.schemas import UserLeaderboardSchema
from app.user.models import User
from app.records.redis_services import global_stats_service, ranking_service

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
