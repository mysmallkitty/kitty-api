from datetime import datetime
from typing import List, Optional

from pydantic import AliasPath, BaseModel, Field, HttpUrl


class RecordPost(BaseModel):
    model_config = {"from_attributes": True}
    deaths: int
    attempts: int
    clear_time: int