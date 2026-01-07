from fastapi import APIRouter, HTTPException, Depends , Body

from fastapi.security import OAuth2PasswordRequestForm
from app.user.model import User
from app.user.service.token import create_access_token, create_refresh_token, decode_token, get_current_user
from tortoise.exceptions import DoesNotExist
import settings
from app.user.schemas.token import TokenResponse, TokenRefreshRequest
from app.user.schemas.user import UserMe

router = APIRouter(
    prefix="/api/v1/users",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user: User = await User.get(login_id=form_data.username)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Invalid login ID or password")

    if not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Invalid login ID or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in= settings.JWT_ACCESS_MINUTES * 60,
        refresh_expires_in=settings.JWT_REFRESH_DAYS * 24 * 60 * 60
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
        refresh_expires_in=settings.JWT_REFRESH_DAYS * 24 * 60 * 60
    )

@router.post("/me", response_model=UserMe)
async def get_user(user: User = Depends(get_current_user)):
    return await UserMe.from_user(user)