from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl


class MapListSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    creator: str = Field(validation_alias=AliasPath("creator", "username"))
    title: str
    level: int
    is_ranked: bool
    thumbnail_url: HttpUrl
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
    level: int
    leaderboard: list[LeaderboardEntrySchema]

    @classmethod
    def from_map_records(cls, map_obj, records):
        leaderboard_data = [
            LeaderboardEntrySchema(
                rank=i,
                user_id=r.user.id,
                username=r.user.username,
                deaths=r.deaths,
                clear_time=r.clear_time,
                created_at=r.created_at
            )
            for i, r in enumerate(records, start=1)
        ]
        
        map_obj.leaderboard = leaderboard_data
        
        return cls.model_validate(map_obj)