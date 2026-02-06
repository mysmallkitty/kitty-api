from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from app.records.redis_services import ccu_service, ranking_service
import httpx
from tortoise.exceptions import DoesNotExist, IntegrityError
from app.maps.dependencies import get_valid_map
from app.records.models import Record, Stat
from app.records.schemas import UserRecordListResponse
from app.user.service.user import get_filtered_users_service
import settings
from app.maps.models import Map
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from app.user.models import FriendRequest, FriendRequestStatus, Friendship, User
from app.user.schemas.token import TokenRefreshRequest, TokenResponse
from app.user.schemas.user import UserFilterSchema, UserListResponse, UserMe, UserOut, UserRegisterSchema, UserUpdateSchema
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
    get_optional_user_from_token,
)
from utils import TimeUtil, generate_svg_sprite

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


# 사용자 검색
@router.get("", response_model=UserListResponse, include_in_schema=False)
async def get_users_no_slash(
    params: UserFilterSchema = Depends(),
    user: Optional[User] = Depends(get_optional_user_from_token),
):
    return await get_filtered_users_service(params, user)


@router.get("/", response_model=UserListResponse)
async def get_users(
    params: UserFilterSchema = Depends(),
    user: Optional[User] = Depends(get_optional_user_from_token),
):
    return await get_filtered_users_service(params, user)


@router.get("/online", response_model=UserListResponse)
async def get_online_users(limit: int = 20, offset: int = 0):
    online_ids = await ccu_service.get_online_user_ids()
    total = len(online_ids)
    if not online_ids or offset >= total:
        return {"total": total, "items": []}

    page_ids = online_ids[offset : offset + limit]
    users = await User.filter(id__in=page_ids).only(
        "id",
        "profile_sprite",
        "username",
        "country",
        "level",
        "total_pp",
    )
    if not users:
        return {"total": total, "items": []}

    rank_map = await ranking_service.get_ranks_batch(page_ids)
    user_map = {user.id: user for user in users}

    items = []
    for uid in page_ids:
        user = user_map.get(uid)
        if not user:
            continue
        items.append(
            {
                "id": user.id,
                "profile_sprite": user.profile_sprite,
                "username": user.username,
                "rank": rank_map.get(user.id) or 0,
                "country": user.country,
                "level": user.level,
            }
        )

    return {"total": total, "items": items}


# 사용자 프로필 조회
@router.get("/{user_id}", response_model=UserOut)
async def get_user_profile(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await UserOut.from_user(user)


@router.get("/{user_id}/records", response_model=UserRecordListResponse)
async def get_user_records(user_id: int, limit: int = 100):
    limit = max(1, min(int(limit), 100))
    records = (
        await Record.filter(
            user_id=user_id,
            map__is_ranked=True,
            pp__not_isnull=True,
        )
        .select_related("map", "map__creator")
        .order_by("-pp")
        .limit(limit)
    )
    items = []
    for record in records:
        map_obj = record.map
        if map_obj is None:
            continue
        creator = map_obj.creator.username if getattr(map_obj, "creator", None) else ""
        items.append(
            {
                "map": {
                    "id": map_obj.id,
                    "title": map_obj.title,
                    "creator": creator,
                },
                "pp": float(record.pp or 0.0),
                "clear_time": record.clear_time,
                "deaths": record.deaths,
                "created_at": record.created_at,
            }
        )
    return {"items": items}

# 친구 요청
@router.post("/friends/request/{target_id}")
async def send_friend_request(target_id: int, current_user: User = Depends(get_current_user)):
    if target_id == current_user.id:
        raise HTTPException(status_code=400, detail="can't friend yourself.")

    if await Friendship.filter(user=current_user, friend_id=target_id).exists():
        raise HTTPException(status_code=400, detail="already friends.")

    existing_request = await FriendRequest.filter(
        from_user=current_user, 
        to_user_id=target_id,
        status=FriendRequestStatus.PENDING
    ).exists()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="already sent a friend request.")

    await FriendRequest.create(from_user=current_user, to_user_id=target_id)
    return {"send friend request successfully."}

# 친구 수락
@router.post("/friends/accept/{request_id}")
async def accept_friend_request(request_id: int, current_user: User = Depends(get_current_user)):
    request = await FriendRequest.get_or_none(id=request_id, to_user=current_user)
    
    if not request or request.status != FriendRequestStatus.PENDING:
        raise HTTPException(status_code=404, detail="not valid request.")

    async with in_transaction():
        request.status = FriendRequestStatus.ACCEPTED
        await request.save()

        await Friendship.get_or_create(user_id=request.from_user_id, friend_id=request.to_user_id)
        await Friendship.get_or_create(user_id=request.to_user_id, friend_id=request.from_user_id)

    return {"accept friend request successfully."}

# 친구 거절
@router.post("/friends/reject/{request_id}")
async def reject_friend_request(
    request_id: int, 
    current_user: User = Depends(get_current_user)
):
    request = await FriendRequest.get_or_none(id=request_id, to_user=current_user)
    
    if not request:
        raise HTTPException(
            status_code=404, 
            detail={"code": "NOT_FOUND", "message": "Friend request not found."}
        )

    if request.status != FriendRequestStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail={
                "code": "ALREADY_PROCESSED", 
                "message": f"This request is already {request.status}."
            }
        )

    request.status = FriendRequestStatus.REJECTED
    await request.save()

    return "Friend request has been rejected."

# 친구 삭제
@router.delete("/friends/{friend_id}")
async def unfriend(friend_id: int, current_user: User = Depends(get_current_user)):
    deleted_count = await Friendship.filter(
        (Q(user=current_user, friend_id=friend_id) | Q(user_id=friend_id, friend=current_user))
    ).delete()

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, 
            detail="You are not friends with this user."
        )

    return {"Unfriended successfully."}

# 친구 목록
@router.get("/friends")
async def get_my_friend_list(current_user: User = Depends(get_current_user)):
    friendships = await Friendship.filter(user=current_user).prefetch_related("friend")
    if not friendships:
        return []

    friend_ids = [f.friend.id for f in friendships]
    online_set = await ccu_service.get_online_ids(friend_ids)
    rank_map = await ranking_service.get_ranks_batch(friend_ids)

    results = []

    for f in friendships:
        friend = f.friend
        
        results.append({
            "id": friend.id,
            "username": friend.username,
            "is_online": friend.id in online_set,
            "rank": rank_map.get(friend.id, "Unranked"),
            "last_active_display": TimeUtil.format_last_active(friend.last_login_at)
        })

    return results 

@router.get("/{user_id}/sprite.svg")
async def get_user_sprite(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user or not user.profile_sprite:
        return Response(status_code=404)
    svg_code = generate_svg_sprite(user.profile_sprite)
    return Response(content=svg_code, media_type="image/svg+xml")