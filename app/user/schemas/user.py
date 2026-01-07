from pydantic import BaseModel

from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from app.user.model import User, Friendship

UserOut = pydantic_model_creator(User, name="UserOut")

class UserMe(UserOut):
    friend_count: int

    @classmethod
    async def from_user(cls, user: User) -> "UserMe":
        base = await UserOut.from_tortoise_orm(user)
        cnt = await Friendship.filter(user=user).count()
        return cls.model_validate({**base.model_dump(), "friend_count": cnt})