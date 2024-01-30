from typing import Any

from redis.asyncio import Redis

from geo.utils.redis import RedisClient


class RedisQueue:
    def __init__(self, client: Redis | RedisClient | Any, namespace: str = 'queue'):
        self._client = client
        self.key = namespace

    async def enqueue(self, *values: bytes | memoryview | str | int | float) -> None:
        await self._client.rpush(self.key, *values)

    async def dequeue(self) -> str | list | None:
        return await self._client.lpop(self.key)

    async def is_empty(self) -> bool:
        return await self._client.llen(self.key) == 0

    async def close(self) -> None:
        await self._client.close()
