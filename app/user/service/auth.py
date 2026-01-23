from typing import Optional
from fastapi import HTTPException
import httpx

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