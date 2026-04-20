from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..infrastructure.database.session import async_session_factory
from ..infrastructure.cache.redis_client import RedisClient
from ..infrastructure.cache.rating_cache import RatingCacheService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_cache() -> RatingCacheService:
    client = await RedisClient.get_client()
    return RatingCacheService(client)

