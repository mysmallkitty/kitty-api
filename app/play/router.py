from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.play.schemas import RoomCreate
from app.play.websocket import verify_websocket_token, websocket_game_handler
from app.play.service import room_service
from app.user.models import User
from app.records.redis_services import ranking_service


router = APIRouter(
    prefix="/api/v1",
    tags=["play"],
    responses={404: {"description": "Not found"}},
)


security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return await verify_websocket_token(credentials.credentials)


@router.websocket("/{map_id}/play")
async def play_map(websocket: WebSocket, map_id: int, token: str, room_id: str | None = None):
    await websocket_game_handler(websocket, map_id, token, room_id)

# 방 생성
@router.post("/rooms")
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(get_current_user),
):
    host_info = {
        "profile_sprite": current_user.profile_sprite,
        "rank": ranking_service.get_rank(current_user)
    }

    room = await room_service.create_room(
        title=room_data.title,
        map_id=room_data.map_id,
        host_id=current_user.id,
        host_name=current_user.username,
        host_info=host_info,
        max_players=room_data.max_players
    )
    return room

# 방 목록 조회
@router.get("/rooms")
async def get_rooms():
    rooms = await room_service.get_all_rooms()
    return {"rooms": rooms}

# 방 정보
@router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = await room_service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="can't find room")
    return room

# 방 참가
@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str, 
    current_user: User = Depends(get_current_user)
):
    info = {
        "sprite": current_user.profile_sprite,
        "rank": ranking_service.get_rank(current_user)
    }
    return await room_service.join_room(room_id, current_user.id, current_user.username, info)

# 방 나가기
@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
):
    result = await room_service.leave_room(room_id, current_user.id)
    return result