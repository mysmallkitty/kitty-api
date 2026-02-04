from typing import Optional

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

from app.maps.models import Map


async def get_valid_map_with_creator(map_id: int):
    map_obj = await Map.get_or_none(id=map_id).prefetch_related("creator")

    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found.")

    return map_obj


async def get_valid_map(map_id: int, is_ranked: bool = False) -> Map:
    map_obj = (
        await Map.filter(id=map_id)
        .only("id", "title")
        .first()
    )
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found.")
    if is_ranked and not map_obj.is_ranked:
        raise HTTPException(status_code=400, detail="Map is not ranked.")
    return map_obj
