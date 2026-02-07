import json
from fastapi import FastAPI, HTTPException, logger
from pydantic import BaseModel
import redis.asyncio as redis
import uuid
import time
from typing import List, Optional

from app.play import manager

rd = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class RoomService:
    @staticmethod
    def _room_key(room_id: str) -> str:
        return f"room:{room_id}"
    
    @staticmethod
    def _room_players_key(room_id: str) -> str:
        return f"room:{room_id}:players"
    
    @staticmethod
    async def create_room(
        title: str,
        map_id: int,
        host_id: int,
        host_name: str,
        host_info: dict,
        max_players: int = 4
    ) -> dict:
        room_id = str(uuid.uuid4())[:8]
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = {
            "id": room_id,
            "title": title,
            "map_id": str(map_id),
            "host_id": str(host_id),
            "host_name": host_name,
            "max_players": str(max_players),
            "status": "waiting",
            "created_at": str(time.time())
        }
        
        player_data = {
            "user_id": host_id,
            "username": host_name,
            "profile_sprite": host_info.get("profile_sprite", ""),
            "rank": host_info.get("rank", 0),
            "is_ready": True,
            "is_host": True
        }

        async with rd.pipeline(transaction=True) as pipe:
            pipe.hset(room_key, mapping=room_data)
            pipe.expire(room_key, 7200)
            pipe.hset(players_key, str(host_id), json.dumps(player_data))
            pipe.expire(players_key, 7200)
            pipe.sadd("lobby:rooms", room_id)
            await pipe.execute()
        
        return await RoomService.get_room(room_id)
    
    @staticmethod
    async def get_room(room_id: str) -> Optional[dict]:
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = await rd.hgetall(room_key)
        if not room_data:
            return None
        
        players_raw = await rd.hgetall(players_key)
        players = []
        for p_str in players_raw.values():
            p_data = json.loads(p_str)
            players.append(p_data)
        
        return {
            "id": room_data["id"],
            "title": room_data["title"],
            "map_id": int(room_data["map_id"]),
            "host_id": int(room_data["host_id"]),
            "host_name": room_data["host_name"],
            "players": players,
            "current_players": len(players),
            "max_players": int(room_data["max_players"]),
            "status": room_data["status"],
            "created_at": float(room_data["created_at"])
        }
    
    @staticmethod
    async def get_all_rooms() -> List[dict]:
        room_ids = await rd.smembers("lobby:rooms")
        rooms = []
        
        for room_id in room_ids:
            room = await RoomService.get_room(room_id)
            if room:
                rooms.append(room)
            else:
                await rd.srem("lobby:rooms", room_id)
        
        return rooms
    
    @staticmethod
    async def join_room(room_id: str, user_id: int, username: str, info: dict) -> dict:
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = await rd.hgetall(room_key)
        if not room_data:
            raise HTTPException(status_code=404, detail="can't find room")
        
        if room_data["status"] != "waiting":
            raise HTTPException(status_code=400, detail="already started")
        
        current_count = await rd.hlen(players_key)
        max_players = int(room_data["max_players"])
        
        if current_count >= max_players:
            raise HTTPException(status_code=400, detail="room is full")
        
        is_already_joined = await rd.hexists(players_key, str(user_id))
        if is_already_joined:
            raise HTTPException(status_code=400, detail="already joined")
        
        player_data = {
            "user_id": user_id,
            "username": username,
            "profile_sprite": info.get("profile_sprite", ""),
            "rank": info.get("rank", 0),
            "is_ready": False,
            "is_host": False
        }
        await rd.hset(RoomService._room_players_key(room_id), str(user_id), json.dumps(player_data))
        return await RoomService.get_room(room_id)

    @staticmethod
    async def leave_room(room_id: str, user_id: int):
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = await rd.hgetall(room_key)
        if not room_data:
            raise HTTPException(status_code=404, detail="can't find room")
        
        await rd.hdel(players_key, str(user_id))
        remaining = await rd.hlen(players_key)
        
        if remaining == 0:
            await RoomService.delete_room(room_id)
            return {"action": "deleted", "message": "room deleted"}
        
        if int(room_data.get("host_id", 0)) == user_id:
            all_players = await rd.hgetall(players_key)
            if all_players:
                new_host_id = list(all_players.keys())[0]
                new_host_data = json.loads(all_players[new_host_id]) 
                new_host_data["is_host"] = True
                
                async with rd.pipeline(transaction=True) as pipe:
                    pipe.hset(room_key, mapping={
                        "host_id": new_host_id,
                        "host_name": new_host_data["username"]
                    })
                    pipe.hset(players_key, new_host_id, json.dumps(new_host_data))
                    await pipe.execute()
                    
        return {"action": "left", "message": "left room"}
    
    @staticmethod
    async def kick_player(room_id: str, host_id: int, target_user_id: int):
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = await rd.hgetall(room_key)
        if not room_data:
            raise HTTPException(status_code=404, detail="can't find room")
            
        if int(room_data["host_id"]) != host_id:
            raise HTTPException(status_code=403, detail="only host can kick player")
            
        if host_id == target_user_id:
            raise HTTPException(status_code=400, detail="can't kick yourself")
            
        deleted = await rd.hdel(players_key, str(target_user_id))
        if not deleted:
            raise HTTPException(status_code=404, detail="user not found in room")
            
    @staticmethod
    async def delete_room(room_id: str):
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        async with rd.pipeline(transaction=True) as pipe:
            pipe.delete(room_key)
            pipe.delete(players_key)
            pipe.srem("lobby:rooms", room_id)
            await pipe.execute()
    
    @staticmethod
    async def update_ready_status(room_id: str, user_id: int, is_ready: bool):
        players_key = RoomService._room_players_key(room_id)
        player_json = await rd.hget(players_key, str(user_id))
        
        if not player_json:
            raise HTTPException(status_code=404, detail="Player not found")
        
        player_data = json.loads(player_json)
        player_data["is_ready"] = is_ready
        
        await rd.hset(players_key, str(user_id), json.dumps(player_data))
        
    @staticmethod
    async def start_game(room_id: str, host_id: int):
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)
        
        room_data = await rd.hgetall(room_key)
        if not room_data:
            raise HTTPException(status_code=404, detail="can't find room")
        
        if int(room_data["host_id"]) != host_id:
            raise HTTPException(status_code=403, detail="only host can start game")

        all_players = await rd.hgetall(players_key)
        for player_str in all_players.values():
            player = json.loads(player_str)
            if not player["is_host"] and not player["is_ready"]:
                raise HTTPException(
                    status_code=400, 
                    detail="all players must be ready to start the game"
                )
        
        await rd.hset(room_key, "status", "playing")

    @staticmethod
    async def finish_game(room_id: str):
        room_key = RoomService._room_key(room_id)
        players_key = RoomService._room_players_key(room_id)

        room_data = await rd.hgetall(room_key)
        if not room_data:
            return

        players = await rd.hgetall(players_key)
        if not players:
            return

        async with rd.pipeline(transaction=True) as pipe:
            pipe.hset(room_key, "status", "waiting")

            for uid, p in players.items():
                data = json.loads(p)
                data["is_ready"] = False
                pipe.hset(players_key, uid, json.dumps(data))

            await pipe.execute()
    
        
room_service = RoomService()

async def check_and_finish_game(session_id: str):
    session = manager.get_session(session_id)
    if not session or not session.room_id:
        return
    
    group_key = (session.map_id, session.room_id)
    all_sessions = []
    
    for sid in manager.game_groups.get(group_key, []):
        s = manager.get_session(sid)
        if s:
            all_sessions.append(s)
    
    if not all_sessions:
        return
    
    all_cleared = all(s.is_cleared for s in all_sessions)
    
    if all_cleared:
        results = []
        for s in all_sessions:
            player_result = {
                "user_id": s.user_id,
                "username": s.username,
                "deaths": s.deaths,
                "is_cleared": s.is_cleared,
                "place": s.place or 0,
                "clear_time": s.clear_time,
                "play_time": int(time.time() - s.start_time)
            }
            results.append(player_result)
        
        results.sort(key=lambda x: x["clear_time"] if x["clear_time"] else float('inf'))
        
        finish_message = {
            "type": "game_finished",
            "results": results,
            "map_id": session.map_id,
            "room_id": session.room_id,
            "reason": "all_cleared" 
        }
        
        await manager.broadcast_to_group(group_key, finish_message)
        
        await room_service.finish_game(session.room_id)

        for s in all_sessions:
          s.started = False
          s.is_cleared = False
          s.clear_time = None
          s.place = None
          s.deaths = 0
          s.start_time = time.time()
        
        logger.info(f"Game auto-finished: room {session.room_id} - all players cleared")