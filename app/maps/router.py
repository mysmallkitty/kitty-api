from fastapi import APIRouter, Depends
from app.maps.models import Map
from app.maps.schemas import MapListSchema, MapDetailSchema, MapUpdateSchema, MapCreateSchema
from app.user.models import User
from app.user.service.token import get_current_user
from fastapi import HTTPException

router = APIRouter(
    prefix="/api/v1/maps",
    tags=["maps"],
    responses={404: {"description": "Not found"}},
)

# 맵 목록 조회
@router.get("/", response_model=list[MapListSchema])
async def get_maps():
    maps = await Map.all().prefetch_related("creator")
    return maps

# 맵 업로드
@router.post("/", response_model=MapDetailSchema)
async def create_map(
    map_data: MapCreateSchema,
    current_user: User = Depends(get_current_user)  # 인증된 유저
):
    if await Map.filter(title=map_data.title).exists():
        raise HTTPException(status_code=400, detail="이미 존재하는 제목입니다")

    new_map = await Map.create(
        title=map_data.title,
        detail=map_data.detail,
        level=map_data.level,
        thumbnail_url=map_data.thumbnail_url,
        map_url=map_data.map_url,
        creator=current_user
    )

    await new_map.fetch_related("creator")

    return new_map

# 맵 상세 조회
@router.get("/{map_id}", response_model=MapDetailSchema)
async def get_map_detail(map_id: int):
    map_obj = await Map.get_or_none(id=map_id)

    if not map_obj:
        raise HTTPException(status_code=404, detail="맵을 찾을 수 없습니다")

    await map_obj.fetch_related("creator")
    return map_obj

# 맵 수정
@router.patch("/{map_id}", response_model=MapDetailSchema)
async def update_map(
    map_id: int,
    map_data: MapUpdateSchema,
    current_user: User = Depends(get_current_user)
):
    map_obj = await Map.get_or_none(id=map_id).prefetch_related("creator")
    if not map_obj:
        raise HTTPException(status_code=404, detail="맵을 찾을 수 없습니다.")

    if map_obj.creator.id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    update_data = map_data.model_dump(exclude_unset=True)

    await map_obj.update_from_dict(update_data)
    await map_obj.save()

    return map_obj

