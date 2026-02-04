from typing import Optional
from fastapi import HTTPException
import httpx

from app.user.models import Roles, User

PROFILE_ALPHABET_32 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
PROFILE_ALPHABET_64 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
PLAYER_ALPHABET_64 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
PLAYER_ALPHABET_32 = PLAYER_ALPHABET_64[:32]


def _validate_profile_sprite(user: User, sprite: str) -> None:
    if sprite is None:
        return
    if len(sprite) != 256:
        raise HTTPException(status_code=400, detail="Invalid profile sprite length.")
    
    allowed = PROFILE_ALPHABET_64 if user.role == Roles.SUPPORT.value else PROFILE_ALPHABET_32
    for ch in sprite:
        if ch not in allowed:
            raise HTTPException(status_code=400, detail="Invalid profile sprite data.")

def _validate_player_sprite(user: User, sprite: str) -> None:
    if sprite is None:
        return
    if len(sprite) <= 72:
        prefix = "0"
        data = sprite
    elif len(sprite) >= 73:
        prefix = sprite[0]
        data = sprite[1:]
    else:
        raise HTTPException(status_code=400, detail="Invalid player sprite length.")
    if prefix not in ("0", "1"):
        raise HTTPException(status_code=400, detail="Invalid player sprite prefix.")
    if prefix == "1" and user.role != Roles.SUPPORT.value:
        raise HTTPException(status_code=403, detail="Supporter role required.")

    allowed = PLAYER_ALPHABET_64 if prefix == "1" else PLAYER_ALPHABET_32
    for ch in data:
        if ch not in allowed:
            raise HTTPException(status_code=400, detail="Invalid player sprite data.")


async def validate_username_unique(username: str, current_user_id: int = None):
    existing = await User.get_or_none(username=username)
    if existing and existing.id != current_user_id:
        raise HTTPException(status_code=400, detail="Already In Use Username.")


async def update_user(user: User, update_dict: dict) -> User:
    if "username" in update_dict:
        await validate_username_unique(update_dict["username"], user.id)

    if "password" in update_dict:
        user.set_password(update_dict.pop("password"))

    if "profile_sprite" in update_dict:
        _validate_profile_sprite(user,update_dict.get("profile_sprite"))

    if "player_sprite" in update_dict:
        _validate_player_sprite(user, update_dict.get("player_sprite"))

    if update_dict:
        user.update_from_dict(update_dict)

    await user.save()
    return user


import httpx
from typing import Optional


async def get_client_country(ip: str) -> Optional[str]:

    async with httpx.AsyncClient() as client:
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,countryCode"
            response = await client.get(url, timeout=2.0)
            data = response.json()

            if data.get("status") == "success":
                country = data.get("countryCode")
                return country.lower() if country else None

            return None

        except Exception:
            return None
