import asyncio
import logging
import pickle
from uuid import UUID

from geo.models.schemas import TaskState
from geo.models.schemas.tomography import TomographyProc
from geo.utils.redis import RedisClient
from geo.utils.redis_queue import RedisQueue


async def worker(redis_client: RedisClient, redis_data_base: RedisClient, queue: RedisQueue):
    while True:
        await asyncio.sleep(3)
        task_id_str = await queue.dequeue()
        if not task_id_str:
            continue

        task_id = UUID(task_id_str)
        if not await redis_client.exists(str(task_id)):
            logging.error(f"[TomographyProc] Задача с id {task_id!r} не существует, но существовала в очереди")
            continue

        raw_obj = await redis_data_base.get(f"{task_id_str}:tomography")
        if not raw_obj:
            logging.error(f"[TomographyProc] Данные задачи с id {task_id!r} не существуют, но существовали ранее")
            await redis_client.hset(str(task_id), {"status": TaskState.FAILED.value})
            continue
        data = TomographyProc.model_validate(pickle.loads(bytes.fromhex(raw_obj)))
        print("worker 2")
