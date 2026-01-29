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


async def get_valid_map(map_id: int, is_ranked: bool = False) -> Map:
    map_obj = await Map.filter(id=map_id).only("id", "title", "map_url", "preview_url", "is_ranked").first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found.")
    if is_ranked and not map_obj.is_ranked:
        raise HTTPException(status_code=400, detail="Map is not ranked.")
    return map_obj
