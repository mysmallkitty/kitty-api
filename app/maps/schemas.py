from datetime import datetime

from pydantic import BaseModel, field_validator, computed_field, Field
from typing import List, Optional


class CreatorBase(BaseModel):
    creator: str

    @field_validator("creator", mode="before")
    @classmethod
    def extract_nickname(cls, v):
        return getattr(v, "nickname", "")

class MapListSchema(CreatorBase):
    id: int
    title: str
    level: int
    thumbnail_url: str
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
    map_url: str
    thumbnail_url: str | None
    is_ranked: bool
    is_wip: bool
    created_at: datetime
    updated_at: datetime

class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str
    level: float = Field(..., ge=1, le=10)
    thumbnail_url: str
    map_url: str = Field(...)

class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    level: Optional[float] = Field(None, ge=1, le=10)
    thumbnail_url: Optional[str] = None
    file_url: Optional[str] = None
    is_wip: Optional[bool] = None
