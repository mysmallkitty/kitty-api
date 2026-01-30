from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field

MIN_RATING = 1.0
MAX_RATING = 8.0


class MapListSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
    rating: float = Field(ge=MIN_RATING, le=MAX_RATING)
    is_ranked: bool
    loved_count: int = Field(ge=0)
    total_attempts: int = Field(ge=0)
    thumbnail_url: Optional[str] = Field(
        None, validation_alias=AliasPath("preview_url")
    )


class MapDetailSchema(MapListSchema):
    detail: str
    map_url: str
    thumbnail_url: Optional[str] = Field(
        None, validation_alias=AliasPath("preview_url")
    )
    total_deaths: int = Field(ge=0)
    total_attempts: int = Field(ge=0)
    total_clears: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime
    loved_count: int = Field(ge=0)


class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str = Field(..., max_length=100)
    rating: float = Field(..., ge=MIN_RATING, le=MAX_RATING)


class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    rating: Optional[float] = Field(ge=MIN_RATING, le=MAX_RATING)


class LeaderboardEntrySchema(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    rank: int = 0
    user_id: int = Field(validation_alias=AliasPath("user", "id"))
    username: str = Field(validation_alias=AliasPath("user", "username"))
    deaths: int = Field(ge=0)
    pp: float = Field(ge=0.0)
    clear_time: int
    created_at: datetime


class MapLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    level: float = Field(validation_alias=AliasPath("rating"), ge=0)
    leaderboard: list[LeaderboardEntrySchema]

    @classmethod
    def from_map_records(cls, map_obj, records):
        leaderboard_data = [
            LeaderboardEntrySchema.model_validate({**r.__dict__, "rank": i})
            for i, r in enumerate(records, start=1)
        ]

        map_obj.leaderboard = leaderboard_data

        return cls.model_validate(map_obj)
