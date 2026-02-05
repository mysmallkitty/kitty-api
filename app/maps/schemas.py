from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field

MIN_RATING = 0.0
MAX_RATING = 11.0


class MapListSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
    rating: float = Field(ge=MIN_RATING, le=MAX_RATING)
    is_ranked: bool
    loved_count: int
    total_attempts: int = 0
    hash: str = ""
    is_loved: bool = False
    pp: float = Field(0.0, ge=0.0)

class MapListResponse(BaseModel):
    total: int
    items: list[MapListSchema]


class MapDetailSchema(MapListSchema):
    user_attempts: int = 0
    user_deaths: int = 0
    best_time: int | None = None
    is_loved: bool = False
    detail: str
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
    profile_sprite: Optional[str] = Field(None, validation_alias=AliasPath("user", "profile_sprite"))
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
        leaderboard_data = []
        for i, r in enumerate(records, start=1):
            user_id = r.user.id if getattr(r, "user", None) else r.user_id
            username = r.user.username if getattr(r, "user", None) else None
            data = {
                "rank": i,
                "user_id": user_id,
                "username": username,
                "profile_sprite": r.user.profile_sprite if getattr(r, "user", None) else None,
                "deaths": r.deaths,
                "pp": r.pp,
                "clear_time": r.clear_time,
                "created_at": r.created_at,
            }
            entry = LeaderboardEntrySchema.model_validate(data)
            leaderboard_data.append(entry)

        map_obj.leaderboard = leaderboard_data

        return cls.model_validate(map_obj)

class MapFilterSchema(BaseModel):
    title: Optional[str] = None
    creator: Optional[str] = None
    map_id: Optional[int] = None

    sort: str = "latest"  # latest | plays | loved | rating

    ranked_only: bool = False
    loved_only: bool = False

    rating_min: Optional[float] = None
    rating_max: Optional[float] = None

    offset: int = 0
    size: int = Field(20, gt=0, le=100)
