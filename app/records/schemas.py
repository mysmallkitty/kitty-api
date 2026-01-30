from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl


class RecordPost(BaseModel):
    model_config = {"from_attributes": True}
    deaths: int = Field(ge=0)
    attempts: int = Field(ge=0)
    clear_time: int


from pydantic import BaseModel


class UserLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}
    username: str
    profile_img_url: str | None
    country: str | None
    total_pp: float = Field(ge=0)
    total_clears: int = Field(ge=0)
