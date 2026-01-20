from typing import Optional
from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import (pydantic_model_creator,
                                       pydantic_queryset_creator)

from app.user.models import Friendship, User

UserOut = pydantic_model_creator(User, name="UserOut")


class UserMe(UserOut):
    friend_count: int
    rank: int

    @classmethod
    async def from_user(cls, user: User) -> "UserMe":
        base = await UserOut.from_tortoise_orm(user)
        friend_count = await Friendship.filter(user=user).count()
        rank = await User.filter(skill_level__gt=user.skill_level).count() + 1
        return cls.model_validate(
            {**base.model_dump(), "friend_count": friend_count, "rank": rank}
        )
    

class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=100)
    profile_img_url: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=3)