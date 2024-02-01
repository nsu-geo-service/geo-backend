import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from geo.repositories import TaskRepo
from geo.repositories.tomography import TomographyRepo
from geo.utils.queue import Queue


async def worker(queue: Queue, lazy_session: async_sessionmaker[AsyncSession]):
    task_id = queue.dequeue()
    if not task_id:
        return

    logging.info(f"[TomographyProc] Получена задача с id {task_id!r}")
    async with lazy_session() as session:
        task_repo = TaskRepo(session)
        tomography_repo = TomographyRepo(session)

        task = await task_repo.get(id=task_id)
        if not task:
            logging.error(f"[TomographyProc] Задача с id {task_id!r} не существует")
            return

        data = await tomography_repo.get(task_id=task_id)
        if not data:
            logging.error(f"[TomographyProc] Данные задачи с task_id {task_id!r} не существуют")
            return


