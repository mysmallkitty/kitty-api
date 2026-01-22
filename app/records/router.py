from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.maps.dependencies import get_valid_map, get_valid_map_with_creator
from app.maps.models import Map
from app.records.models import Record, Stat
from app.user.service.token import get_current_user

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)


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


# 맵 좋아요
@router.post("/{map_id}/like")
async def toggle_like(
    map_obj: Map = Depends(get_valid_map), user=Depends(get_current_user)
):
    async with in_transaction():
        stat, created = await Stat.get_or_create(
            user=user, map=map_obj, defaults={"is_loved": True}
        )

        if created or not stat.is_loved:
            stat.is_loved = True
            is_loved = True
            await Map.filter(id=map_obj.id).update(loved_count=F("loved_count") + 1)
        else:
            stat.is_loved = False
            is_loved = False
            await Map.filter(id=map_obj.id, loved_count__gt=0).update(
                loved_count=F("loved_count") - 1
            )

        await stat.save()

    return {
        "is_loved": is_loved,
    }
