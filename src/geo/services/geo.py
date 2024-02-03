from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from geo.exceptions import NotFound, BadRequest
from geo.models.schemas import TaskID, TaskState, TaskStep
from geo.models.schemas.seisdata import SeisData
from geo.models.schemas.event import Event
from geo.models.schemas.station import Station
from geo.models.schemas.tomography import Tomography
from geo.repositories import TaskRepo
from geo.repositories.event import EventRepo
from geo.repositories.seisdata import SeisDataRepo
from geo.repositories.station import StationRepo
from geo.repositories.tomography import TomographyRepo
from geo.services.storage import FileStorage
from geo.utils.queue import Queue


class GeoApplicationService:

    def __init__(
            self,
            data_queue: Queue,
            tomography_queue: Queue,
            lazy_session: async_sessionmaker[AsyncSession],
            storage: FileStorage
    ):
        self._seisdata_queue = data_queue
        self._tomography_queue = tomography_queue
        self._lazy_session = lazy_session
        self._storage = storage

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

            if task.state != TaskState.PENDING and task.step != TaskStep.SEISDATA:
                raise BadRequest(f"Задача с id {task_id!r} уже находится в обработке или завершена")

            await tomography_repo.create(**data.model_dump(), task_id=task_id)
            await task_repo.update(id=task_id, state=TaskState.IN_PROGRESS)
            self._tomography_queue.enqueue(task_id)

    async def events(self, task_id: TaskID) -> list[Event]:
        async with self._lazy_session() as session:
            event_repo = EventRepo(session)
            events = await event_repo.get_all(
                task_id=task_id
            )
        return [Event.model_validate(event) for event in events]

    async def stations(self, task_id: TaskID) -> list[Station]:
        async with self._lazy_session() as session:
            station_repo = StationRepo(session)
            stations = await station_repo.get_all(
                task_id=task_id
            )
        return [Station.model_validate(station) for station in stations]

    async def tomography_vtk_3d(self, task_id: TaskID):
        async with self._lazy_session() as session:
            tomography_repo = TomographyRepo(session)
            task_repo = TaskRepo(session)
            tomography = await tomography_repo.get(task_id=task_id)
            task = await task_repo.get(id=task_id)

        if not tomography:
            raise NotFound(f"Данные задачи с task_id {task_id!r} не существуют")
        if task.state != TaskState.DONE:
            raise BadRequest(f"Задача с id {task_id!r} не завершена")
        return self._storage.load_gen(f"{task_id}/model.vtk", "rb")

    async def tomography_in_h5(self, task_id: TaskID):
        async with self._lazy_session() as session:
            tomography_repo = TomographyRepo(session)
            task_repo = TaskRepo(session)
            tomography = await tomography_repo.get(task_id=task_id)
            task = await task_repo.get(id=task_id)

        if not tomography:
            raise NotFound(f"Данные задачи с task_id {task_id!r} не существуют")
        if task.state != TaskState.DONE:
            raise BadRequest(f"Задача с id {task_id!r} не завершена")
        return self._storage.load_gen(f"{task_id}/input.h5", "rb")

    async def tomography_out_h5(self, task_id: TaskID):
        async with self._lazy_session() as session:
            tomography_repo = TomographyRepo(session)
            task_repo = TaskRepo(session)
            tomography = await tomography_repo.get(task_id=task_id)
            task = await task_repo.get(id=task_id)

        if not tomography:
            raise NotFound(f"Данные задачи с task_id {task_id!r} не существуют")
        if task.state != TaskState.DONE:
            raise BadRequest(f"Задача с id {task_id!r} не завершена")
        return self._storage.load_gen(f"{task_id}/output.h5", "rb")