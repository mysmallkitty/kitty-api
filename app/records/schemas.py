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
