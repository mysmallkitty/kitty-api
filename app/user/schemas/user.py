from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.records.redis_services import ranking_service
from app.user.models import Friendship, User

UserOutBase = pydantic_model_creator(User, name="UserOutBase")


class UserOut(UserOutBase):
    rank: int = Field(ge=0, default=0)
    total_pp: float = Field(ge=0.0, default=0.0)

    @classmethod
    async def from_user(cls, user: User) -> "UserOut":
        base = await UserOutBase.from_tortoise_orm(user)
        rank = await ranking_service.get_rank(user.id)
        return cls.model_validate({**base.model_dump(), "rank": rank if rank else 0})


class UserMe(UserOut):
    friend_count: int = Field(ge=0)
    rank: int = Field(ge=0)

    @classmethod
    async def from_user(cls, user: User) -> "UserMe":
        base = await UserOutBase.from_tortoise_orm(user)
        friend_count = await Friendship.filter(user=user).count()
        rank = await ranking_service.get_rank(user.id)
        return cls.model_validate(
            {**base.model_dump(), "friend_count": friend_count, "rank": rank if rank else 0}
        )


class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: str = Field("optional@email.com", max_length=100)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=100)
    profile_sprite: Optional[str] = Field(None, max_length=256)
    player_sprite: Optional[str] = Field(None, max_length=81)
