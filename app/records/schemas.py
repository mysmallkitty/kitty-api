from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl, field_validator

class RecordPost(BaseModel):
    model_config = {"from_attributes": True}
    deaths: int = Field(ge=0)
    attempts: int = Field(ge=0)
    clear_time: int

class UserLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int = Field(ge=0, default=0)
    rank: int = Field(ge=0, default=0)
    username: str
    profile_sprite: str = ""
    total_pp: float = Field(ge=0)
    total_clears: int = Field(ge=0)

    @field_validator("profile_sprite", mode="before")
    @classmethod
    def _profile_sprite_default(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value)


class UserRecordMapSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    creator: str = ""

    @field_validator("creator", mode="before")
    @classmethod
    def _creator_default(cls, value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            username = value.get("username")
            return "" if username is None else str(username)
        return str(value)


class UserRecordSchema(BaseModel):
    model_config = {"from_attributes": True}
    map: UserRecordMapSchema
    pp: float = Field(ge=0.0)
    clear_time: int | None = None
    deaths: int = Field(ge=0)
    created_at: datetime


class UserRecordListResponse(BaseModel):
    items: list[UserRecordSchema]
