from pydantic import BaseModel

from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from app.user.models import User, Friendship

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
