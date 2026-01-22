from fastapi import HTTPException

from app.user.models import User


async def validate_username_unique(username: str, current_user_id: int = None):
    existing = await User.get_or_none(username=username)
    if existing and existing.id != current_user_id:
        raise HTTPException(status_code=400, detail="Already In Use Username.")


async def update_user(user: User, update_dict: dict) -> User:
    if "username" in update_dict:
        await validate_username_unique(update_dict["username"], user.id)

    if "password" in update_dict:
        user.set_password(update_dict.pop("password"))

    if update_dict:
        user.update_from_dict(update_dict)

    await user.save()
    return user
