from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field


class MapListSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
<<<<<<< HEAD
    rating: float
    level: float = Field(validation_alias=AliasPath("rating"))
    is_ranked: bool
    loved_count: int
    total_attempts: int = 0
=======
    rating: float = Field(ge=1.0, le=8.0)
    is_ranked: bool
    loved_count: int = Field(ge=0)
    download_count: int = Field(ge=0)


# 맵 상세 조회
>>>>>>> cd00c99a59cd915ffa9261afbe8d19979829bbed


class MapDetailSchema(MapListSchema):
    detail: str
<<<<<<< HEAD
    total_deaths: int
    total_attempts: int
    total_clears: int
=======
    map_url: HttpUrl
    total_deaths: int = Field(ge=0)
    total_attempts: int = Field(ge=0)
    total_clears: int = Field(ge=0)
    rating: float = Field(ge=1.0, le=8.0)
>>>>>>> cd00c99a59cd915ffa9261afbe8d19979829bbed
    created_at: datetime
    updated_at: datetime
    loved_count: int = Field(ge=0)
    download_count: int = Field(ge=0)


class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str = Field(..., max_length=100)
    rating: float = Field(..., ge=1.0, le=8.0)


class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    rating: Optional[float] = Field(None, ge=1.0, le=8.0)

class LeaderboardEntrySchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True 
    }

    rank: int = 0
    user_id: int = Field(validation_alias=AliasPath("user", "id"))
    username: str = Field(validation_alias=AliasPath("user", "username"))
    deaths: int = Field(ge=0)
    pp: float = Field(ge=0)
    clear_time: int
    created_at: datetime

class MapLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
<<<<<<< HEAD
    level: float = Field(validation_alias=AliasPath("rating"))
=======
    level: float = Field(ge=1.0, le=8.0)
>>>>>>> cd00c99a59cd915ffa9261afbe8d19979829bbed
    leaderboard: list[LeaderboardEntrySchema]

    @classmethod
    def from_map_records(cls, map_obj, records):
        leaderboard_data = [
            LeaderboardEntrySchema.model_validate(
                {**r.__dict__, "rank": i}
            )
            for i, r in enumerate(records, start=1)
        ]
        
        map_obj.leaderboard = leaderboard_data

        return cls.model_validate(map_obj)
