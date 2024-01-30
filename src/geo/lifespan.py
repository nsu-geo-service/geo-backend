import logging

from redis.asyncio import Redis
from fastapi import FastAPI

from geo.config import Config, RedisConfig
from geo.utils.redis import RedisClient
from geo.utils.redis_queue import RedisQueue


async def init_redis_pool(app: FastAPI, config: RedisConfig):
    pool_0 = await Redis.from_url(
        f"redis://{config.HOST}:{config.PORT}/0",
        encoding="utf-8",
        decode_responses=True,
    )
    pool_1 = await Redis.from_url(
        f"redis://{config.HOST}:{config.PORT}/1",
        encoding="utf-8",
        decode_responses=True,
    )
    getattr(app, "state").redis_client = RedisClient(pool_0)
    getattr(app, "state").data_queue = RedisQueue(pool_1, namespace="data_queue")
    getattr(app, "state").tomography_queue = RedisQueue(pool_1, namespace="tomography_queue")


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
        await getattr(self._app, "state").redis_client.close()
        await getattr(self._app, "state").data_queue.close()
        await getattr(self._app, "state").tomography_queue.close()
