from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl


class MapListSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
    level: float
    is_ranked: bool
    preview: str | None
    loved_count: int 
    download_count: int


class MapDetailSchema(MapListSchema):
    detail: str
    map_url: HttpUrl
    total_deaths: int
    total_attempts: int
    total_clears: int
    created_at: datetime
    updated_at: datetime


# 맵 등록
class MapCreateSchema(BaseModel):
    title: str = Field(..., max_length=50)
    detail: str = Field(..., max_length=500)
    level: float = Field(..., ge=1.0, le=8.0)
    preview: str | None
    map_url: HttpUrl


# 맵 정보 수정
class MapUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    detail: Optional[str] = None
    level: Optional[float] = Field(None, ge=1.0, le=8.0)
    preview: Optional[str] = None
    map_url: Optional[HttpUrl] = None
    is_wip: Optional[bool] = None


# 내 맵 조회
class UserMapItemSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    level: float
    preview: str | None
    loved_count: int
    download_count: int


class UserMapsListSchema(BaseModel):
    id: int
    maps: list[UserMapItemSchema]


# 맵 리더보드 상위 20 명
class LeaderboardEntrySchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True 
    }

    rank: int = 0
    user_id: int = Field(validation_alias=AliasPath("user", "id"))
    username: str = Field(validation_alias=AliasPath("user", "username"))
    deaths: int
    clear_time: int
    created_at: datetime

class MapLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    level: float
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