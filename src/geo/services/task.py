import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from geo.exceptions import NotFound
from geo.models.schemas import TaskID, Task, TaskState
from geo.repositories import TaskRepo


class TaskApplicationService:

    def __init__(
            self,
            lazy_session: async_sessionmaker[AsyncSession],
    ):
        self._lazy_session = lazy_session

    async def list(self, page: int, per_page: int) -> list[Task]:
        per_page_limit = 40

        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            tasks = await task_repo.get_all(offset=offset, limit=per_page, order_by='created_at')

        return [Task.model_validate(task) for task in tasks]

    async def get_task(self, task_id: TaskID) -> Task:
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            task = await task_repo.get(id=task_id)
        if not task:
            raise NotFound(f"Задача с id {task_id!r} не найдена")
        return Task.model_validate(task)

    async def new_task(self) -> Task:
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            task = await task_repo.create(
                state=TaskState.PLAIN,
                created_at=datetime.datetime.now(tz=datetime.UTC)
            )
        return Task.model_validate(task)

    async def delete_task(self, task_id: TaskID) -> None:
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            task = await task_repo.get(id=task_id)
            if not task:
                raise NotFound(f"Задача с id {task_id!r} не найдена")
            await task_repo.delete(id=task_id)

    async def count(self) -> int:
        async with self._lazy_session() as session:
            task_repo = TaskRepo(session)
            count = await task_repo.count()
        return count
