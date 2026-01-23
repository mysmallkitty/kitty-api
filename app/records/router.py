from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.maps.dependencies import get_valid_map, get_valid_map_with_creator
from app.maps.models import Map
from app.records.models import Record, Stat
from app.records.schemas import RecordPost
from app.user.service.token import get_current_user
from app.records.pp.calculate_pp import calculate_pp

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)

# make a record
@router.post("/{map_id}/clear")
async def record_clear(
    record_data: RecordPost,
    map_obj: Map = Depends(get_valid_map, is_ranked=True),
    current_user=Depends(get_current_user),
):
    async with in_transaction():
        stat, _ = await Stat.get_or_create(user=current_user, map=map_obj)
        stat.is_cleared = True
        stat.attempts += 1
        await stat.save()
        map_obj.total_clears = F("total_clears") + 1
        await map_obj.save()
        pp=calculate_pp(
            death_meter=map_obj.death_meter,
            clear_time_meter=map_obj.clear_time_meter,
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



# @router.post("/{map_id}/attempt")
# async def record_attempt(map_id: int, user=Depends(get_current_user)):
#     map = await Map.get_or_none(id=map_id)
#     if not map:
#         raise HTTPException(status_code=404, detail="Map not found")

#     stat, _ = await Stat.get_or_create(user=user, map=map)
#     stat.attempts += 1
#     await stat.save()

#     map.total_attempts += 1
#     await map.save()

#     return {"message": "Attempt recorded"}


# @router.post("/{map_id}/death")
# async def record_death(map_id: int, user=Depends(get_current_user)):
#     map = await Map.get_or_none(id=map_id)
#     if not map:
#         raise HTTPException(status_code=404, detail="Map not found")

#     stat, _ = await Stat.get_or_create(user=user, map=map)
#     stat.deaths += 1
#     stat.attempts += 1
#     await stat.save()

#     map.total_deaths += 1
#     map.total_attempts += 1
#     await map.save()

#     return {"message": "Death recorded"}

