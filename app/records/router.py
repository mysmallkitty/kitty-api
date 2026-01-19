from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.maps.dependencies import get_valid_map
from app.maps.models import Map
from app.records.models import Stat
from app.user.service.token import get_current_user

router = APIRouter(
    prefix="/api/v1/records",
    tags=["records"],
    responses={404: {"description": "Not found"}},
)


@router.post("/attempt/{map_id}")
async def record_attempt(map_id: int, user=Depends(get_current_user)):
    map = await Map.get_or_none(id=map_id)
    if not map:
        raise HTTPException(status_code=404, detail="Map not found")

    stat, _ = await Stat.get_or_create(user=user, map=map)
    stat.total_attempts += 1
    await stat.save()

    map.total_attempts += 1
    await map.save()

    return {"message": "Attempt recorded"}


@router.post("/death/{map_id}")
async def record_death(map_id: int, user=Depends(get_current_user)):
    map = await Map.get_or_none(id=map_id)
    if not map:
        raise HTTPException(status_code=404, detail="Map not found")

    stat, _ = await Stat.get_or_create(user=user, map=map)
    stat.total_deaths += 1
    stat.total_attempts += 1
    await stat.save()

    map.total_deaths += 1
    map.total_attempts += 1
    await map.save()

    return {"message": "Death recorded"}


# 맵 좋아요
@router.post("/like/{map_id}")
async def toggle_like(
    map_obj: Map = Depends(get_valid_map), user=Depends(get_current_user)
):
    async with in_transaction():
        map_obj = await Map.select_for_update().get(id=map_obj.id)
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
