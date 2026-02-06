import asyncio
import datetime
import time
from typing import Union

import redis.asyncio as redis
from settings import REDIS_URL

from app.records.pp.total_pp import recompute_total_pp
from app.user.models import User


class RankingService:
    def __init__(self):
        # redis-py 5 enforces keyword-only args; use from_url to accept the URL form
        self.redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        self.key = "global_leaderboard"

    async def rebuild_leaderboard(self, recompute_pp: bool = False) -> int:
        if recompute_pp:
            user_ids = await User.all().values_list("id", flat=True)
            for user_id in user_ids:
                new_total_pp = await recompute_total_pp(user_id)
                await User.filter(id=user_id).update(total_pp=new_total_pp)

        users = await User.all().only("id", "total_pp")
        await self.redis.delete(self.key)
        if not users:
            return 0
        payload = {str(user.id): float(user.total_pp) for user in users}
        await self.redis.zadd(self.key, payload)
        return len(payload)

    async def update_user_pp(self, user_id: int, total_pp: float):
        await self.redis.zadd(self.key, {str(user_id): total_pp})

    async def get_rank(self, user_id: int) -> int | None:
        rank = await self.redis.zrevrank(self.key, str(user_id))
        return rank + 1 if rank is not None else None

    async def get_leaderboard_page(self, offset: int, limit: int):
        end = max(offset + limit - 1, 0)
        return await self.redis.zrevrange(self.key, offset, end, withscores=True)
    
    async def get_ranks_batch(self, user_ids: list[int]) -> dict[int, int | None]:
        if not user_ids:
            return {}

        async with self.redis.pipeline(transaction=False) as pipe:
            for uid in user_ids:
                pipe.zrevrank(self.key, str(uid))
            raw_ranks = await pipe.execute()

        return {
            uid: (rank + 1 if rank is not None else None)
            for uid, rank in zip(user_ids, raw_ranks)
        }


ranking_service = RankingService()


class GlobalStatsService:
    def __init__(self):
        self.redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        self.key_prefix = "deaths:bucket:"
        self.bucket_size = 600
        self.window_size = 86400

    def _get_bucket_id(self, timestamp: float) -> int:
        return (int(timestamp) // self.bucket_size) * self.bucket_size

    async def record_deaths(self, count: int):
        if count <= 0:
            return

        now = time.time()
        bucket_id = self._get_bucket_id(now)
        key = f"{self.key_prefix}{bucket_id}"

        await self.redis.incrby(key, count)
        await self.redis.expire(key, self.window_size + self.bucket_size)

    async def get_recent_deaths(self) -> int:
        now = time.time()
        current_bucket = self._get_bucket_id(now)

        keys = [
            f"{self.key_prefix}{current_bucket - (i * self.bucket_size)}"
            for i in range(144)
        ]

        values = await self.redis.mget(keys)
        total = sum(int(v) for v in values if v is not None)
        return total


global_stats_service = GlobalStatsService()

class CCUService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.key = "global:online_users"
        self.ttl = 30 
        self._cleanup_task = None

    async def ping(self, identifier: Union[int, str]):
        await self.redis.zadd(self.key, {str(identifier): time.time()})

    async def get_ccu(self) -> int:
        cutoff = time.time() - self.ttl
        return await self.redis.zcount(self.key, cutoff, "+inf")

    async def get_online_ids(self, user_ids: list[int]) -> set[int]:
        if not user_ids:
            return set()

        async with self.redis.pipeline(transaction=False) as pipe:
            for uid in user_ids:
                pipe.zscore(self.key, f"user:{uid}")
            scores = await pipe.execute()

        now = time.time()
        return {
            uid for uid, score in zip(user_ids, scores) 
            if score and score > (now - self.ttl)
        }

    async def get_online_user_ids(self) -> list[int]:
        cutoff = time.time() - self.ttl
        raw_ids = await self.redis.zrevrangebyscore(self.key, "+inf", cutoff)
        user_ids: list[int] = []
        for ident in raw_ids:
            if not isinstance(ident, str):
                continue
            if not ident.startswith("user:"):
                continue
            try:
                user_ids.append(int(ident.split(":", 1)[1]))
            except (ValueError, IndexError):
                continue
        return user_ids
    
    async def _cleanup_loop(self):
        while True:
            cutoff = time.time() - self.ttl
            await self.redis.zremrangebyscore(self.key, "-inf", cutoff)
            await asyncio.sleep(10)

    def start_cleanup(self):
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())


ccu_service = CCUService(REDIS_URL)
