from fastapi import APIRouter, Depends, Query
from app.maps.models import Map
from app.maps.schemas import MapListSchema, MapDetailSchema, MapUpdateSchema, MapCreateSchema
from app.user.models import User
from app.user.service.token import get_current_user
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from tortoise.expressions import F
from tortoise.exceptions import IntegrityError
from typing import Optional
from app.maps.dependencies import MapFilterParams
import app.maps.services as service


router = APIRouter(
    prefix="/api/v1/maps",
    tags=["maps"],
    responses={404: {"description": "Not found"}},
)

# 맵 목록 조회
@router.get("/", response_model=list[MapListSchema])
async def get_maps(params: MapFilterParams = Depends()):
    maps = await service.get_filtered_maps(params)
    return maps

# 맵 업로드
@router.post("/")
async def create_map(
    map_data: MapCreateSchema,
    current_user: User = Depends(get_current_user)  # 인증된 유저
):
    try:
        new_map = await Map.create(
            title=map_data.title,
            detail=map_data.detail,
            level=map_data.level,
            thumbnail_url=map_data.thumbnail_url,
            map_url=map_data.map_url,
            creator=current_user
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="중복된 제목입니다.")

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

# 맵 다운로드
@router.get("/maps/{map_id}/download")
async def download_map(map_id: int):
    updated_count = await Map.filter(id=map_id).update(download_count=F("download_count") + 1)
    
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="맵을 찾을 수 없습니다.")

    map_data = await Map.filter(id=map_id).values("map_url", "title")
    target_map = map_data[0]

    def iterfile():
        with open(target_map["map_url"], mode="rb") as f:
            while chunk := f.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        iterfile(), 
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={target_map['title']}.map"}
    )

# 