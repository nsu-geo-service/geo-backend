from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from geo.exceptions import NotFound, BadRequest
from geo.models.schemas import TaskID, TaskState, TaskStep
from geo.models.schemas.data import SeisData
from geo.models.schemas.tomography import Tomography
from geo.repositories import TaskRepo
from geo.repositories.seisdata import SeisDataRepo
from geo.repositories.tomography import TomographyRepo
from geo.utils.queue import Queue


class GeoApplicationService:

    def __init__(
            self,
            data_queue: Queue,
            tomography_queue: Queue,
            lazy_session: async_sessionmaker[AsyncSession],
    ):
        self._seisdata_queue = data_queue
        self._tomography_queue = tomography_queue
        self._lazy_session = lazy_session

    async def seisdata(self, task_id: TaskID) -> SeisData:
        async with self._lazy_session() as session:
            seisdata_repo = SeisDataRepo(session)
            seisdata = await seisdata_repo.get(task_id=task_id)
        if not seisdata:
            raise NotFound(f"Данные задачи с task_id {task_id!r} не существуют")
        return SeisData.model_validate(seisdata)

    async def tomography(self, task_id: TaskID) -> Tomography:
        async with self._lazy_session() as session:
            tomography_repo = TomographyRepo(session)
            tomography = await tomography_repo.get(task_id=task_id)
        if not tomography:
            raise NotFound(f"Данные задачи с task_id {task_id!r} не существуют")
        return Tomography.model_validate(tomography)

    async def seisdata_proc(self, task_id: TaskID, data: SeisData):
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            seisdata_repo = SeisDataRepo(session)
            task = await task_repo.get(id=task_id)

            if not task:
                raise NotFound(f"Задача с id {task_id!r} не существует")

            if task.state != TaskState.PLAIN:
                raise BadRequest(f"Задача с id {task_id!r} уже находится в обработке или завершена")

            await seisdata_repo.create(**data.model_dump(), task_id=task_id)
            await task_repo.update(id=task_id, state=TaskState.IN_PROGRESS)
            self._seisdata_queue.enqueue(task_id)

    async def tomography_proc(self, task_id: TaskID, data: Tomography):
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            tomography_repo = TomographyRepo(session)
            task = await task_repo.get(id=task_id)

            if not task:
                raise NotFound(f"Задача с id {task_id!r} не существует")

            if task.state != TaskState.PLAIN:
                raise BadRequest(f"Задача с id {task_id!r} уже находится в обработке или завершена")

            await tomography_repo.create(**data.model_dump(), task_id=task_id)
            await task_repo.update(id=task_id, state=TaskState.IN_PROGRESS)
            self._tomography_queue.enqueue(task_id)
