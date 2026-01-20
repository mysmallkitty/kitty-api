from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, computed_field, field_validator


class CreatorBase(BaseModel):
    creator: str

    @field_validator("creator", mode="before")
    @classmethod
    def extract_username(cls, v):
        return getattr(v, "username", "")


class MapListSchema(CreatorBase):
    id: int
    title: str
    level: float
    thumbnail_url: HttpUrl
    loved_count: int
    download_count: int


class MapStatsSchema(BaseModel):
    total_attempts: int
    total_deaths: int
    total_clears: int
    loved_count: int
    download_count: int


class MapDetailSchema(MapStatsSchema, CreatorBase):
    model_config = {"from_attributes": True}

    id: int
    title: str
    detail: str
    level: float
    map_url: HttpUrl
    thumbnail_url: HttpUrl | None
    is_ranked: bool
    is_wip: bool
    created_at: datetime
    updated_at: datetime

# 맵 등록
class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str = Field(..., max_length=500)
    level: float = Field(..., ge=1, le=10)
    thumbnail_url: HttpUrl | None
    map_url: HttpUrl

# 맵 정보 수정
class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    level: Optional[float] = Field(None, ge=1, le=10)
    thumbnail_url: Optional[HttpUrl] = None
    file_url: Optional[HttpUrl] = None
    is_wip: Optional[bool] = None


# 내 맵 조회
class UserMapItemSchema(BaseModel):
    id: int
    title: str
    level: float
    thumbnail_url: HttpUrl | None
    loved_count: int
    download_count: int

class UserMapsListSchema(BaseModel):
    id: int
    maps: list[UserMapItemSchema]