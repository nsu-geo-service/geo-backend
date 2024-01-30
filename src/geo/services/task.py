import asyncio
import uuid
import datetime

from geo.exceptions import NotFound
from geo.models.schemas import TaskID, Task, TaskState, TaskStep
from geo.utils.redis import RedisClient


class TaskApplicationService:

    def __init__(
            self,
            redis_client: RedisClient,
            redis_query_base: RedisClient,
    ):
        self._redis_client = redis_client
        self._redis_query_base = redis_query_base

    async def list(self, page: int, per_page: int) -> list[Task]:
        per_page_limit = 40

        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        sorted_tasks = await self._redis_client.zrange('tasks', 0, -1, with_scores=True)
        trimmed_task_ids = [item[0] for item in sorted_tasks[offset:offset + per_page]]

        raw_tasks = await asyncio.gather(
            *[
                self._redis_client.hgetall(hash_key=task_id)
                for task_id in trimmed_task_ids
            ]
        )

        return [
            Task(
                id=TaskID(uuid.UUID(task_id)),
                state=TaskState(raw_task['state']),
                step=TaskStep(raw_task['step']) if raw_task['step'] else None,
                created_at=datetime.datetime.fromtimestamp(
                    float(raw_task['created_at']),
                    tz=datetime.UTC
                ),
                completed_in=datetime.datetime.fromtimestamp(
                    float(raw_task['completed_in']),
                    tz=datetime.UTC
                ) if raw_task['completed_in'] else None,
            )
            for task_id, raw_task in zip(trimmed_task_ids, raw_tasks)
        ]

    async def get_task(self, task_id: TaskID) -> Task:
        raw_task = await self._redis_client.hgetall(hash_key=str(task_id))
        if not raw_task:
            raise NotFound(f"Задача с id {task_id!r} не найдена")
        return Task(
            id=task_id,
            state=TaskState(raw_task['state']),
            step=TaskStep(raw_task['step']) if raw_task['step'] else None,
            created_at=datetime.datetime.fromtimestamp(
                float(raw_task['created_at']),
                tz=datetime.UTC
            ),
            completed_in=datetime.datetime.fromtimestamp(
                float(raw_task['completed_in']),
                tz=datetime.UTC
            ) if raw_task['completed_in'] else None,
        )

    async def new_task(self) -> Task:
        task = Task(
            id=TaskID(uuid.uuid4()),
            state=TaskState.PLAIN,
            step=None,
            created_at=datetime.datetime.now(tz=datetime.UTC),
            completed_in=None,
        )
        await self._redis_client.hset(
            hash_key=str(task.id),
            mapping={
                'state': task.state.value,
                'step': task.step.value if task.step else '',
                'created_at': task.created_at.timestamp(),
                'completed_in': task.completed_in.timestamp() if task.completed_in else '',
            }
        )
        await self._redis_client.zadd('tasks', {str(task.id): task.created_at.timestamp()})
        return task

    async def delete_task(self, task_id: TaskID) -> None:
        key_exists = await self._redis_client.exists(str(task_id))
        if not key_exists:
            raise NotFound(f"Задача с id {task_id!r} не найдена")

        await self._redis_client.zrem('tasks', str(task_id))
        await self._redis_client.delete(str(task_id))
        await self._redis_query_base.delete(f'{str(task_id)}:data')
        await self._redis_query_base.delete(f'{str(task_id)}:tomography')

    async def count(self) -> int:
        return await self._redis_client.zcard('tasks')
