from fastapi import APIRouter

from app.records.models import Record, Stat
from app.records.schemas import RecordPost
from app.user.service.token import get_current_user
from app.records.pp.calculate_pp import calculate_pp
from app.records.schemas import UserLeaderboardSchema
from app.user.models import User
from tortoise.transactions import in_transaction
from app.maps.dependencies import get_valid_map
from app.maps.models import Map
from fastapi import Depends

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)

# make a record
@router.post("/{map_id}/clear")
async def record_clear(
    record_data: RecordPost,
    map_id: int,
    current_user = Depends(get_current_user),
):
    async with in_transaction():
        map_obj = await get_valid_map(map_id, True)
        stat, _ = await Stat.get_or_create(user=current_user, map=map_obj)
        stat.is_cleared = True
        stat.attempts += 1
        await stat.save()
        map_obj.total_clears = map_obj.total_clears + 1
        await map_obj.save()
        pp=calculate_pp(
            death_meter=map_obj.death_meter,
            deaths=record_data.deaths,
            clear_time=record_data.clear_time,
        )
    await Record.create(
        user=current_user,
        map=map_obj,
        deaths=record_data.deaths,
        clear_time=record_data.clear_time,
        pp=pp
        )
    return {"message": "clear recorded to server", "pp": pp}



# 전체 유저 리더보드 (PP순)
@router.get("/leaderboard", response_model=list[UserLeaderboardSchema])
async def get_global_leaderboard(page: int = 1, limit: int = 50):
    offset = (page - 1) * limit
    return await User.all().order_by("-total_pp").offset(offset).limit(limit)


