from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
import httpx
from tortoise.exceptions import DoesNotExist, IntegrityError
from app.maps.dependencies import get_valid_map
from app.records.models import Stat
import settings
from app.maps.models import Map
from tortoise.expressions import F
from app.user.models import User
from app.user.schemas.token import TokenRefreshRequest, TokenResponse
from app.user.schemas.user import UserMe, UserOut, UserRegisterSchema, UserUpdateSchema
from app.user.service.auth import (
    get_client_country,
    update_user,
    validate_username_unique,
)
from app.user.service.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user: User = await User.get(username=form_data.username)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Invalid Username")

    if not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Wrong Password")

    user.last_login_at = datetime.now()
    await user.save(update_fields=["last_login_at"])

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_MINUTES * 60,
        refresh_expires_in=settings.JWT_REFRESH_DAYS * 24 * 60 * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: TokenRefreshRequest):
    token_config = decode_token(request.refresh_token, expected_type="refresh")
    access_token = create_access_token(token_config.id, scopes=token_config.scopes)
    refresh_token = create_refresh_token(token_config.id, scopes=token_config.scopes)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_MINUTES * 60,
        refresh_expires_in=settings.JWT_REFRESH_DAYS * 24 * 60 * 60,
    )


# 회원가입
@router.post("/signup", response_model=UserOut, status_code=201)
async def signup(request: Request, user_data: UserRegisterSchema):

    await validate_username_unique(user_data.username)

    user = User(username=user_data.username, email=user_data.email)
    user.set_password(user_data.password)
    user.country = await get_client_country(request.client.host)
    try:
        await user.save()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already In Use Username.")

    return await UserOut.from_user(user)


# 내 정보 조회
@router.get("/me", response_model=UserMe)
async def get_user(user: User = Depends(get_current_user)):
    return await UserMe.from_user(user)


# 내 정보 수정
@router.patch("/me", response_model=UserOut)
async def update_user_profile(
    user_data: UserUpdateSchema, current_user: User = Depends(get_current_user)
):
    update_dict = user_data.model_dump(exclude_unset=True)
    updated_user = await update_user(current_user, update_dict)
    return await UserOut.from_user(updated_user)


# 유저 프로필 조회
@router.get("/{user_id}", response_model=UserOut)
async def get_user_profile(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserOut.from_user(user)
