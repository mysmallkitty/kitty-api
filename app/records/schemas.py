from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl


class RecordPost(BaseModel):
    model_config = {"from_attributes": True}
    deaths: int
    attempts: int
    clear_time: int
from pydantic import BaseModel


class UserLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}
    username: str
    profile_img_url: str | None
    country: str | None
    total_pp: float
    total_clears: int
