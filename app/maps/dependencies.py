from typing import Optional

from fastapi import HTTPException, Query

from app.maps.models import Map


class MapFilterParams:
    def __init__(
        self,
        title: Optional[str] = Query(None),
        creator: Optional[str] = Query(None),
        sort: str = Query("latest"),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
    ):
        self.title = title
        self.creator = creator
        self.sort = sort
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


async def get_valid_map_with_creator(map_id: int):
    map_obj = await Map.get_or_none(id=map_id).prefetch_related("creator")

    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found.")

    return map_obj


async def get_valid_map(map_id: int) -> Map:
    map_obj = await Map.only("id", "title").get_or_none(id=map_id)
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found.")
    return map_obj
