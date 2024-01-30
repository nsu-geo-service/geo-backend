import pickle

from geo.exceptions import NotFound, BadRequest
from geo.models.schemas import TaskID, TaskState, TaskStep
from geo.models.schemas.data import DataProc
from geo.models.schemas.tomography import TomographyProc
from geo.utils.redis import RedisClient
from geo.utils.redis_queue import RedisQueue


class GeoApplicationService:

    def __init__(
            self,
            redis_client: RedisClient,
            data_queue: RedisQueue,
            tomography_queue: RedisQueue,
            redis_query_base: RedisClient,
    ):
        self._redis_client = redis_client
        self._data_queue = data_queue
        self._tomography_queue = tomography_queue
        self._redis_query_base = redis_query_base

    async def data(self, task_id: TaskID) -> DataProc:
        raw_obj = await self._redis_query_base.get(f"{task_id}:data")
        if not raw_obj:
            raise NotFound(f"Данные задачи с id {task_id!r} не существуют")
        obj = pickle.loads(bytes.fromhex(raw_obj))
        return DataProc.model_validate(obj)

    async def tomography(self, task_id: TaskID) -> TomographyProc:
        raw_obj = await self._redis_query_base.get(f"{task_id}:tomography")
        if not raw_obj:
            raise NotFound(f"Данные задачи с id {task_id!r} не существуют")
        obj = pickle.loads(bytes.fromhex(raw_obj))
        return TomographyProc.model_validate(obj)

    async def data_proc(self, task_id: TaskID, data: DataProc):
        task = await self._redis_client.hgetall(str(task_id))
        if not task:
            raise NotFound(f"Задача с id {task_id!r} не существует")

        if task['state'] != TaskState.PLAIN.value:
            raise BadRequest(f"Задача с id {task_id!r} уже находится в обработке или завершена")

        raw_obj = pickle.dumps(data.model_dump()).hex()
        await self._redis_client.hset(str(task_id), {'state': TaskState.IN_PROGRESS.value})
        await self._redis_query_base.set(f"{task_id}:data", raw_obj)
        await self._data_queue.enqueue(str(task_id))

    async def tomography_proc(self, task_id: TaskID, data: TomographyProc):
        task = await self._redis_client.hgetall(str(task_id))
        if not task:
            raise NotFound(f"Задача с id {task_id!r} не существует")

        if task['state'] != TaskState.PENDING.value:
            raise BadRequest(f"Задача с id {task_id!r} уже находится в обработке или завершена")

        if task['step'] != TaskStep.DATA.value:
            raise BadRequest(f"Задача с id {task_id!r} не прошла процесс обработки данных")

        raw_obj = pickle.dumps(data.model_dump())
        await self._redis_client.hset(str(task_id), {'state': TaskState.IN_PROGRESS.value})
        await self._redis_query_base.set(f"{task_id}:tomography", raw_obj)
        await self._tomography_queue.enqueue(str(task_id))
