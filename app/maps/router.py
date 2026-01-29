import os
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from tortoise.exceptions import IntegrityError
from tortoise.expressions import F

from app import records
import app.maps.services as service
from app.maps.dependencies import (MapFilterParams, get_valid_map,
                                   get_valid_map_with_creator)
from app.maps.models import Map
from app.maps.schemas import (LeaderboardEntrySchema, MapCreateSchema,
                              MapDetailSchema, MapLeaderboardSchema,
                              MapListSchema, MapUpdateSchema)
from app.records.models import Record
import settings
from app.user.models import User
from app.user.service.token import get_current_user

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

def save_map_file(map_file: UploadFile,preview_file: UploadFile, map_id: int):
    map_path = settings.storage_path + f"/maps/{map_id}.kittymap"
    preview_path = settings.storage_path + f"/previews/{map_id}.kittymap"
    with open(path, "wb") as buffer:
        buffer.write(map_file.file.read())

# 맵 업로드
@router.post("/")
async def create_map(
    map_data: MapCreateSchema,
    map_file: UploadFile = File(...),
    preview_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),  # 인증된 유저

):
    try:
        new_map = await Map.create(
            title=map_data.title,
            detail=map_data.detail,
            level=map_data.rating,
            creator=current_user,
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already In Use Title.")

    return new_map


# 맵 상세 조회
@router.get("/{map_id}", response_model=MapDetailSchema)
async def get_map_detail(map_obj: Map = Depends(get_valid_map_with_creator)):
    return map_obj


# 맵 수정
@router.patch("/{map_id}", response_model=MapDetailSchema)
async def update_map(
    map_data: MapUpdateSchema,
    current_user: User = Depends(get_current_user),
    map_obj: Map = Depends(get_valid_map_with_creator),
):
    if map_obj.creator.id != current_user.id:
        raise HTTPException(status_code=403, detail="Have No Permission.")

    update_data = map_data.model_dump(exclude_unset=True)

    try:
        await map_obj.update_from_dict(update_data)
        await map_obj.save()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already In Use Title.")

    return map_obj


# 맵 다운로드
@router.get("/{map_id}/download")
async def download_map(map_obj: Map = Depends(get_valid_map)):

    if not os.path.exists(map_obj.map_url):
        raise HTTPException(status_code=404, detail="Map not found.")

    await Map.filter(id=map_obj.id).update(download_count=F("download_count") + 1)
    safe_filename = quote(f"{map_obj.title}.map")

    return FileResponse(
        path=map_obj.map_url,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        },
    )


# 맵 리더보드 상위 20명 뽑기
@router.get("/{map_id}/leaderboard", response_model=MapLeaderboardSchema)
async def get_map_leaderboard(map_obj: Map = Depends(get_valid_map_with_creator)):
    records = await (
        Record.filter(map_id=map_obj.id, clear_time__not_isnull=True)
        .prefetch_related("user")
        .order_by("clear_time")
        .limit(20)
    )

    return MapLeaderboardSchema.from_map_records(map_obj, records)