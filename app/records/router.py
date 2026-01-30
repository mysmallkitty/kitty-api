from fastapi import APIRouter
from app.records.schemas import UserLeaderboardSchema
from app.user.models import User

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
