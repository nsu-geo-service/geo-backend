import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from geo.config import Config
from geo.db import create_sqlite_async_session
from geo.models import tables
from geo.utils.queue import Queue

from geo.services import data_proc
from geo.services import tomography_proc


async def init_db(app: FastAPI, *, echo: bool = False) -> None:
    engine, session = create_sqlite_async_session(
        database="database",
        echo=echo
    )
    getattr(app, "state").db_session = session

    async with engine.begin() as conn:
        # await conn.run_sync(tables.Base.metadata.drop_all)
        await conn.run_sync(tables.Base.metadata.create_all)


def start_workers(app: FastAPI, fdsn_base: str, executable: str):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=data_proc.worker,
        trigger="interval",
        seconds=5,
        args=(
            getattr(app, "state").data_queue,
            getattr(app, "state").db_session,
            getattr(app, "state").http_client,
            fdsn_base
        ),
    )
    scheduler.add_job(
        func=tomography_proc.worker,
        trigger="interval",
        seconds=5,
        args=(
            getattr(app, "state").tomography_queue,
            getattr(app, "state").db_session,
            getattr(app, "state").storage,
            executable
        ),
    )

    logging.getLogger('apscheduler.executors.default').propagate = False
    logging.getLogger('apscheduler.scheduler').propagate = False
    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    scheduler.start()


class LifeSpan:

    def __init__(self, app: FastAPI, config: Config):
        self._app = app
        self._config = config

    async def startup_handler(self) -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        getattr(self._app, "state").data_queue = Queue()
        getattr(self._app, "state").tomography_queue = Queue()
        await init_db(self._app, echo=self._config.DEBUG)
        start_workers(self._app, self._config.FDSN_BASE, self._config.HPS_ST3D_EXEC)
        logging.info("FastAPI Успешно запущен.")

    async def shutdown_handler(self) -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")
