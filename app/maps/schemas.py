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
    level: int
    is_ranked: bool
    thumbnail_url: HttpUrl
    loved_count: int 
    download_count: int


class MapStatsSchema(BaseModel):
    total_deaths: int
    loved_count: int
    download_count: int
    total_attempts: int
    total_clears: int


class MapDetailSchema(MapStatsSchema, CreatorBase):
    model_config = {"from_attributes": True}

    id: int
    title: str
    detail: str
    level: int
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
    level: int = Field(..., ge=1, le=8)
    thumbnail_url: HttpUrl | None
    map_url: HttpUrl


# 맵 정보 수정
class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=8)
    thumbnail_url: Optional[HttpUrl] = None
    file_url: Optional[HttpUrl] = None
    is_wip: Optional[bool] = None


# 내 맵 조회
class UserMapItemSchema(BaseModel):
    id: int
    title: str
    level: int
    thumbnail_url: HttpUrl | None
    loved_count: int
    download_count: int


class UserMapsListSchema(BaseModel):
    id: int
    maps: list[UserMapItemSchema]


# 맵 리더보드 상위 20 명
class LeaderboardEntrySchema(BaseModel):
    model_config = {"from_attributes": True}

    rank: int = 0
    user_id: int
    username: str
    deaths: int
    clear_time: int
    created_at: datetime

    @field_validator("username", mode="before")
    @classmethod
    def extract_username(cls, v):
        if hasattr(v, "username"):
            return v.username
        return v

    @field_validator("user_id", mode="before")
    @classmethod
    def extract_user_id(cls, v):
        if hasattr(v, "id"):
            return v.id
        return v


class MapLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    creator: str
    level: int
    leaderboard: list[LeaderboardEntrySchema]

    @field_validator("creator", mode="before")
    @classmethod
    def extract_username(cls, v):
        return getattr(v, "username", "")
