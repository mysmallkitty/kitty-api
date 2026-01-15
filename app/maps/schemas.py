from datetime import datetime

from pydantic import BaseModel, field_validator, computed_field
from typing import List


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
