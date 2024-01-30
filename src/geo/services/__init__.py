from geo.config import Config
from geo.services.stats import StatsApplicationService
from geo.services.task import TaskApplicationService
from geo.utils.redis import RedisClient


class ServiceFactory:
    def __init__(
            self,
            config: Config,
            redis_queue: RedisClient,
    ):
        self._redis_queue = redis_queue
        self._config = config

    @property
    def task(self) -> TaskApplicationService:
        return TaskApplicationService(
            redis_queue=self._redis_queue,
        )

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(redis_queue=self._redis_queue, config=self._config)
