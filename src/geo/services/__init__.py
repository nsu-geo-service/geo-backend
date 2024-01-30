from geo.config import Config
from geo.services.geo import GeoApplicationService
from geo.services.stats import StatsApplicationService
from geo.services.task import TaskApplicationService
from geo.utils.redis import RedisClient
from geo.utils.redis_queue import RedisQueue


class ServiceFactory:
    def __init__(
            self,
            config: Config,
            redis_client: RedisClient,
            data_queue: RedisQueue,
            tomography_queue: RedisQueue,
    ):
        self._redis_client = redis_client
        self._data_queue = data_queue
        self._tomography_queue = tomography_queue
        self._config = config

    @property
    def task(self) -> TaskApplicationService:
        return TaskApplicationService(
            redis_client=self._redis_client,
        )

    @property
    def geo(self) -> GeoApplicationService:
        return GeoApplicationService(
            redis_client=self._redis_client,
            data_queue=self._data_queue,
            tomography_queue=self._tomography_queue,
        )

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(redis_client=self._redis_client, config=self._config)
