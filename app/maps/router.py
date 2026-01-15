from fastapi import APIRouter
from app.maps.models import Map
from app.maps.schemas import MapListSchema, MapDetailSchema

router = APIRouter(
    prefix="/api/v1/maps",
    tags=["maps"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[MapListSchema])
async def get_maps():
    maps = await Map.all().prefetch_related("creator")
    return maps

@router.get("/{map_id}", response_model=MapDetailSchema)
async def get_map_detail(map_id: int):
    map = await Map.get(id=map_id).prefetch_related("creator")
    return map