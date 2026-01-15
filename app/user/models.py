from hashlib import sha256

from passlib.context import CryptContext
from tortoise import fields
from tortoise.models import Model
import typing

from settings import PASSWORD_SALT

if typing.TYPE_CHECKING:
    pass

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

from enum import Enum


class Roles(str, Enum):
    ADMIN = "admin"  # Administrator (어드민)
    MOD = "mod"  # Moderator (운영자)
    RM = "rm"  # Ranked Manager (맵 랭크하는사람)
    LV = "lv"  # Level Validator (맵 레벨 정하는사람 예: 랭커들, 겜잘알들, 운영자jot목팸들)
    USER = "user"  # Regular User (일반 유저)


class User(Model):

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=100)
    profile_img_url = fields.CharField(max_length=255)
    level = fields.IntField(default=1)
    exp = fields.IntField(default=0)
    country = fields.CharField(max_length=3, null=True)
    total_deaths = fields.IntField(default=0)
    total_attempts = fields.IntField(default=0)
    total_clears = fields.IntField(default=0)
    role = fields.CharField(max_length=10, default=Roles.USER.value)

    skill_level = fields.FloatField(default=0.0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login_at = fields.DatetimeField(null=True)

    class PydanticMeta:
        exclude = ("password",)

    def __str__(self) -> str:
        return self.username

    def _salt_password(self, password: str) -> str:
        salted = f"{password}{PASSWORD_SALT}".encode("utf-8")
        return sha256(salted).hexdigest()

    def set_password(self, password: str) -> None:
        self.password = pwd_context.hash(self._salt_password(password))

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(self._salt_password(password), self.password)

    async def friend_count(self) -> int:
        return await Friendship.filter(user=self).count()


class Friendship(Model):

    id = fields.IntField(pk=True)
    user: User = fields.ForeignKeyField("models.User", related_name="friends")
    friend: User = fields.ForeignKeyField("models.User", related_name="followers")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "friend")
