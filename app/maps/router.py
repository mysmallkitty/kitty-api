import os
import shutil
from hashlib import sha256
from typing import Optional
from urllib.parse import quote
from tortoise.transactions import in_transaction

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import FileResponse
from tortoise.exceptions import IntegrityError
from tortoise.expressions import F

import app.maps.services as service
from app.maps.dependencies import (
    MapFilterParams,
    get_valid_map,
    get_valid_map_with_creator,
)
from app.maps.models import Map
from app.maps.schemas import (
    MapDetailSchema,
    MapListSchema,
    MapUpdateSchema,
    MapCreateSchema,
    MapLeaderboardSchema,
)
from app.records.models import Record, Stat
import settings
from app.user.models import User
from app.user.service.token import get_current_user, decode_token

router = APIRouter(
    prefix="/api/v1/maps",
    tags=["maps"],
    responses={404: {"description": "Not found"}},
)


async def get_optional_user(authorization: str | None = Header(None)) -> User | None:
    if not authorization:
        return None
    if not authorization.lower().startswith('bearer '):
        return None
    token = authorization.split(' ', 1)[1]
    try:
        token_config = decode_token(token, expected_type='access')
    except Exception:
        return None
    return await User.get_or_none(id=token_config.id)

def _ensure_storage_dirs() -> None:
    os.makedirs(os.path.join(settings.storage_path, "maps"), exist_ok=True)
    os.makedirs(os.path.join(settings.storage_path, "previews"), exist_ok=True)


def _map_file_path(map_id: int) -> str:
    return os.path.join(settings.storage_path, "maps", f"{map_id}.kittymap")


def _preview_file_path(map_id: int) -> str:
    return os.path.join(settings.storage_path, "previews", f"{map_id}.kittymap")


def _save_upload_file(upload: UploadFile, path: str) -> bytes:
    try:
        upload.file.seek(0)
    except Exception:
        pass
    data = upload.file.read()
    with open(path, "wb") as buffer:
        buffer.write(data)
    return data


@router.get("/", response_model=list[MapListSchema])
async def get_maps(params: MapFilterParams = Depends()):
    maps = await service.get_filtered_maps(params)
    return maps


@router.post("/", response_model=MapDetailSchema)
async def create_map(
    title: str = Form(...),
    detail: Optional[str] = Form(""),
    rating: float = Form(...),
    map_file: UploadFile = File(...),
    preview_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    _ensure_storage_dirs()
    try:
        new_map = await Map.create(
            title=title,
            detail=detail,
            rating=rating,
            creator=current_user,
            map_url="not-set",
            preview_url="not-set",
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="invalid map data")

    map_path = _map_file_path(new_map.id)
    preview_path = _preview_file_path(new_map.id)

    map_bytes = _save_upload_file(map_file, map_path)
    _save_upload_file(preview_file, preview_path)
    new_map.hash = sha256(map_bytes).hexdigest()

    await new_map.save()
    return new_map


@router.get("/{map_id}", response_model=MapDetailSchema)
async def get_map_detail(
    map_obj: Map = Depends(get_valid_map_with_creator),
    current_user: User | None = Depends(get_optional_user),
):
    if current_user:
        stat = await Stat.get_or_none(user_id=current_user.id, map_id=map_obj.id)
        record = await Record.filter(user_id=current_user.id, map_id=map_obj.id).first()
        map_obj.user_attempts = stat.attempts if stat else 0
        map_obj.user_deaths = stat.deaths if stat else 0
        map_obj.is_loved = stat.is_loved if stat else False
        map_obj.best_time = record.clear_time if record else None
    return map_obj


@router.put("/{map_id}", response_model=MapDetailSchema)
async def update_map_file(
    map_obj: Map = Depends(get_valid_map_with_creator),
    current_user: User = Depends(get_current_user),
    title: Optional[str] = Form(None),
    detail: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    map_file: Optional[UploadFile] = File(None),
    preview_file: Optional[UploadFile] = File(None),
):
    if map_obj.creator.id != current_user.id:
        raise HTTPException(status_code=403, detail="Have No Permission.")

    update_data = {}
    if title is not None:
        update_data["title"] = title
    if detail is not None:
        update_data["detail"] = detail
    if rating is not None:
        update_data["rating"] = rating

    if update_data:
        try:
            await map_obj.update_from_dict(update_data)
            await map_obj.save()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="What")

    _ensure_storage_dirs()
    if map_file is not None:
        map_path = _map_file_path(map_obj.id)
        map_bytes = _save_upload_file(map_file, map_path)
        map_obj.hash = sha256(map_bytes).hexdigest()
    if preview_file is not None:
        preview_path = _preview_file_path(map_obj.id)
        _save_upload_file(preview_file, preview_path)
    await map_obj.save()

    return map_obj


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
        raise HTTPException(status_code=400, detail="invalid map data")

    return map_obj


@router.get("/{map_id}/download")
async def download_map(map_obj: Map = Depends(get_valid_map)):
    map_path = _map_file_path(map_obj.id)
    if not os.path.exists(map_path):
        raise HTTPException(status_code=404, detail="Map not found.")

    await Map.filter(id=map_obj.id).update(total_attempts=F("total_attempts") + 1)
    safe_filename = quote(f"{map_obj.title}.map")

    return FileResponse(
        path=map_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        },
    )


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
            await User.filter(id=user.id).update(total_loved=F("total_loved") + 1)
        else:
            stat.is_loved = False
            is_loved = False
            await Map.filter(id=map_obj.id, loved_count__gt=0).update(
                loved_count=F("loved_count") - 1
            )
            await User.filter(id=user.id, total_loved__gt=0).update(
                total_loved=F("total_loved") - 1
            )

        await stat.save()

    return {
        "is_loved": is_loved,
    }


@router.get("/{map_id}/preview")
async def download_preview(map_obj: Map = Depends(get_valid_map)):
    preview_path = _preview_file_path(map_obj.id)
    if not preview_path or not os.path.exists(preview_path):
        raise HTTPException(status_code=404, detail="Preview not found.")

    safe_filename = quote(f"{map_obj.title}_preview.map")
    return FileResponse(
        path=preview_path,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
        },
    )


@router.get("/{map_id}/leaderboard", response_model=MapLeaderboardSchema)
async def get_map_leaderboard(map_obj: Map = Depends(get_valid_map_with_creator)):
    records = await (
        Record.filter(map_id=map_obj.id, pp__not_isnull=True)
        .prefetch_related("user")
        .order_by("-pp", "clear_time")
        .limit(20)
    )

    return MapLeaderboardSchema.from_map_records(map_obj, records)
