from pydantic import BaseModel


class UserLeaderboardSchema(BaseModel):
    model_config = {"from_attributes": True}
    username: str
    profile_img_url: str | None
    country: str | None
    total_pp: float
    total_clears: int