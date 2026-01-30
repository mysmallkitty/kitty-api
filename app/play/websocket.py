import time
from typing import Dict
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from tortoise.expressions import F
from tortoise.transactions import in_transaction
from app.records.redis_services import global_stats_service
from app.maps.models import Map
from app.records.models import Stat
from app.user.models import User
from app.user.service.token import decode_token
from app.play.manager import manager
from app.play.schemas import SessionStarted, ErrorResponse


async def verify_websocket_token(token: str):
    """WebSocket용 토큰 검증"""
    try:
        token_config = decode_token(token, expected_type="access")
        user = await User.get_or_none(id=token_config.id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


async def handle_session_end(session_id: str):
    session = manager.get_session(session_id)
    if not session or (session.deaths == 0 and not session.is_cleared):
        return
    
    await global_stats_service.record_deaths(session.deaths)

    async with in_transaction():
        stat, _ = await Stat.get_or_create(
            user_id=session.user_id, map_id=session.map_id
        )
        stat.deaths += session.deaths

        await stat.save()

        # session.deaths 만큼 user, map 에 total deaths 추가
        await Map.filter(id=session.map_id).update(
            total_deaths=F("total_deaths") + session.deaths
        )

        await User.filter(id=session.user_id).update(
            total_deaths=F("total_deaths") + session.deaths
        )


async def websocket_game_handler(websocket: WebSocket, map_id: int, token: str):
    await websocket.accept()

    try:
        # 토큰 검증
        user = await verify_websocket_token(token)
    except HTTPException:
        await websocket.send_json(
            ErrorResponse(message="Authentication failed").model_dump()
        )
        await websocket.close(code=1008)
        return

    # 맵 존재 확인
    map_obj = await Map.get_or_none(id=map_id)
    if not map_obj:
        await websocket.send_json(ErrorResponse(message="Map not found").model_dump())
        await websocket.close(code=1008)
        return

    # 세션 생성
    session_id = f"{user.id}_{map_id}_{int(time.time() * 1000)}"
    await manager.connect(websocket, session_id, map_id, user.id)

    try:
        # 맵 시작하면 attemtps 증가 (user, map)
        async with in_transaction():
            stat, _ = await Stat.get_or_create(user_id=user.id, map_id=map_id)
            stat.attempts += 1
            await stat.save()

            await Map.filter(id=map_id).update(total_attempts=F("total_attempts") + 1)
            await User.filter(id=user.id).update(total_attempts=F("total_attempts") + 1)

        # 시작 확인 전송
        await websocket.send_json(
            SessionStarted(session_id=session_id, map_id=map_id).model_dump()
        )

        # 메시지 수신 루프
        while True:
            data = await websocket.receive_json()
            await manager.dispatch(websocket, session_id, data)

    except WebSocketDisconnect:
        # 연결 종료 - 데스 카운트 DB 저장
        await handle_session_end(session_id)

    except Exception as e:
        # 예외 발생 시에도 세션 저장
        await handle_session_end(session_id)
        raise e

    finally:
        # 세션 정리
        await manager.disconnect(session_id)
