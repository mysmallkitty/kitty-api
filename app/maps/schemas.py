from datetime import datetime

from pydantic import BaseModel, field_validator, computed_field, Field, HttpUrl
from typing import List, Optional


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

class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str = Field(..., max_length=500)
    level: float = Field(..., ge=1, le=10)
    thumbnail_url: HttpUrl | None
    map_url: HttpUrl

class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    level: Optional[float] = Field(None, ge=1, le=10)
    thumbnail_url: Optional[HttpUrl] = None
    file_url: Optional[HttpUrl] = None
    is_wip: Optional[bool] = None
