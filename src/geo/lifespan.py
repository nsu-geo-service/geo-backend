import logging

from redis.asyncio import Redis
from fastapi import FastAPI

from geo.config import Config, RedisConfig
from geo.utils.redis import RedisClient


async def init_redis_pool(app: FastAPI, config: RedisConfig):
    pool_0 = await Redis.from_url(
        f"redis://{config.HOST}:{config.PORT}/0",
        encoding="utf-8",
        decode_responses=True,
    )
    getattr(app, "state").redis_queue = RedisClient(pool_0)


class LifeSpan:

    def __init__(self, app: FastAPI, config: Config):
        self._app = app
        self._config = config

    async def startup_handler(self) -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        await init_redis_pool(self._app, self._config.REDIS)
        logging.info("FastAPI Успешно запущен.")

    async def shutdown_handler(self) -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")
        await getattr(self._app, "state").redis_queue.close()
