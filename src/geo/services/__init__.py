from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from geo.config import Config
from geo.services.geo import GeoApplicationService
from geo.services.stats import StatsApplicationService
from geo.services.storage import FileStorage
from geo.services.task import TaskApplicationService
from geo.utils.queue import Queue


class ServiceFactory:
    def __init__(
            self,
            config: Config,
            lazy_session: async_sessionmaker[AsyncSession],
            data_queue: Queue,
            tomography_queue: Queue,
            storage: FileStorage
    ):
        self._lazy_session = lazy_session
        self._data_queue = data_queue
        self._tomography_queue = tomography_queue
        self._config = config
        self._storage = storage

    @property
    def task(self) -> TaskApplicationService:
        return TaskApplicationService(
            lazy_session=self._lazy_session,
        )

    @property
    def geo(self) -> GeoApplicationService:
        return GeoApplicationService(
            data_queue=self._data_queue,
            tomography_queue=self._tomography_queue,
            lazy_session=self._lazy_session,
            storage=self._storage
        )

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(config=self._config)
