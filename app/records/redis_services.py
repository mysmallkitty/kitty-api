import redis.asyncio as redis
from settings import REDIS_URL

import time

class RankingService:
    def __init__(self):
        self.redis = redis.Redis(REDIS_URL, decode_responses=True)
        self.key = "global_leaderboard"

    # 유저의 모든 PP를 Redis Sorted Set에 저장
    async def update_user_pp(self, user_id: int, total_pp: int):
        await self.redis.zadd(self.key, {str(user_id): total_pp})

    # 유저의 현재 순위를 가져옴 (1등부터 시작)
    async def get_rank(self, user_id: int) -> int | None:
        rank = await self.redis.zrevrank(self.key, str(user_id))
        return rank + 1 if rank is not None else None

ranking_service = RankingService()


class GlobalStatsService:
    def __init__(self):
        self.redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        self.key_prefix = "deaths:bucket:"
        self.bucket_size = 600  
        self.window_size = 86400  

    def _get_bucket_id(self, timestamp: float) -> int:
        return (int(timestamp) // self.bucket_size) * self.bucket_size
    
    # 10분 단위 버킷에 저장
    async def record_deaths(self, count: int):
        if count <= 0:
            return

        now = time.time()
        bucket_id = self._get_bucket_id(now)
        key = f"{self.key_prefix}{bucket_id}"

        await self.redis.incrby(key, count)
        
        await self.redis.expire(key, self.window_size + self.bucket_size)

    # 144개 버킷 합산
    async def get_recent_deaths(self) -> int:
        now = time.time()
        current_bucket = self._get_bucket_id(now)
        
        # 최근 144개의 버킷 키 리스트 생성
        keys = [
            f"{self.key_prefix}{current_bucket - (i * self.bucket_size)}"
            for i in range(144)
        ]

        # 여러 키를 한 번에 조회 (MGET)
        values = await self.redis.mget(keys)
        
        # 숫자 합산 (none 값 빼고)
        total = sum(int(v) for v in values if v is not None)
        return total

global_stats_service = GlobalStatsService()