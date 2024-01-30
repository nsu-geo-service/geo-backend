from geo.models.schemas import TaskID, TaskCreate, Task
from geo.utils.redis import RedisClient


class TaskApplicationService:

    def __init__(
            self,
            redis_queue: RedisClient,
    ):
        self._redis_queue = redis_queue

    async def list(self) -> list[Task]:
        ...

    async def get_task(self, task_id: TaskID) -> Task:
        pass

    async def new_task(self, data: TaskCreate) -> Task:
        pass

    async def delete_task(self, task_id: TaskID) -> None:
        pass

    