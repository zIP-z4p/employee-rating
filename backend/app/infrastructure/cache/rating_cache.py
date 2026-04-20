import json
from datetime import date
import redis.asyncio as aioredis
from app.config import get_settings


class RatingCacheService:
    PREFIX = "rating"

    def __init__(self, client: aioredis.Redis):
        self.client = client
        self.ttl = get_settings().CACHE_TTL_SECONDS

    def _snapshot_key(self, period: date, top_n: int | None) -> str:
        return f"{self.PREFIX}:snapshot:{period}:{top_n or 'all'}"

    async def get_snapshot(self, period: date, top_n: int | None) -> list | None:
        key = self._snapshot_key(period, top_n)
        raw = await self.client.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def set_snapshot(self, period: date, top_n: int | None, data: list) -> None:
        key = self._snapshot_key(period, top_n)
        serialized = json.dumps(data, default=str)
        await self.client.setex(key, self.ttl, serialized)

    async def invalidate_period(self, period: date) -> int:
        pattern = f"{self.PREFIX}:*:{period}:*"
        keys = await self.client.keys(pattern)
        if keys:
            return await self.client.delete(*keys)
        return 0

