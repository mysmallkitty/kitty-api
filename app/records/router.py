from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import date
from typing import List, Dict, DefaultDict
from collections import defaultdict

from app.maps.models import Map
from app.records.models import Stat, Record
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
