import asyncio
import logging
import os
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin

import aiofiles
from aiomultiprocess import Worker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from geo.models.schemas import TaskState, TaskStep
from geo.repositories import TaskRepo
from geo.repositories.detection import DetectionRepo
from geo.repositories.event import EventRepo
from geo.repositories.seisdata import SeisDataRepo
from geo.repositories.station import StationRepo
from geo.services.data_proc.utils import (
    quake,
    stations
)
from geo.utils.http import HttpProcessor
from geo.utils.queue import Queue


async def fetch_from_base(http_client: HttpProcessor, url: str, params: dict = None):
    async with http_client as client:
        return await client.get(
            url=url,
            params=params
        )


async def cpu_worker(quake_file: str, station_file: str):
    events, detections = quake(quake_file)
    station_table = stations(station_file)

    return events, detections, station_table


async def worker(
        queue: Queue,
        lazy_session: async_sessionmaker[AsyncSession],
        http_client: HttpProcessor,
        fdsn_base: str

):
    task_id = queue.dequeue()
    if not task_id:
        return

    logging.info(f"[SeisDataProc] Получена задача с id {task_id!r}")
    async with lazy_session() as session:
        task_repo = TaskRepo(session)
        seisdata_repo = SeisDataRepo(session)

        task = await task_repo.get(id=task_id)
        if not task:
            logging.error(f"[SeisDataProc] Задача с id {task_id!r} не существует")
            return

        data = await seisdata_repo.get(task_id=task_id)
        if not data:
            logging.error(f"[SeisDataProc] Данные задачи с task_id {task_id!r} не существуют")
            return

    quake_params = {
        "includeallorigins": "true",
        "includearrivals": "true",
        "includeallmagnitudes": "true",
        "starttime": data.start_time.isoformat(),
        "endtime": data.end_time.isoformat(),
        "nodata": 404,
    }
    if data.min_latitude:
        quake_params["minlatitude"] = data.min_latitude
    if data.max_latitude:
        quake_params["maxlatitude"] = data.max_latitude
    if data.min_longitude:
        quake_params["minlongitude"] = data.min_longitude
    if data.max_longitude:
        quake_params["maxlongitude"] = data.max_longitude

    quake_resp, station_resp = await asyncio.gather(
        fetch_from_base(
            http_client,
            url=urljoin(fdsn_base, "/fdsnws/event/1/query"),
            params=quake_params
        ),
        fetch_from_base(
            http_client,
            url=urljoin(fdsn_base, "/fdsnws/station/1/query"),
            params={
                "network": data.network,
                "nodata": 404,
            }
        )
    )

    station_xml = station_resp.text
    quake_xml = quake_resp.text

    if not station_resp.is_success or not quake_resp.is_success:
        logging.error(f"[SeisDataProc] Ошибка при получении данных станций {station_resp.status_code}")
        async with lazy_session() as session:
            task_repo = TaskRepo(session)
            await task_repo.update(id=task_id, state=TaskState.FAILED)
        return

    quake_file = NamedTemporaryFile(delete_on_close=False)
    station_file = NamedTemporaryFile(delete_on_close=False)

    async with aiofiles.open(station_file.name, 'w') as file:
        await file.write(station_xml)

    async with aiofiles.open(quake_file.name, 'w') as file:
        await file.write(quake_xml)

    logging.info(f"[SeisDataProc] Обработка данных")

    events, detections, station_table = await Worker(
        target=cpu_worker,
        args=(quake_file.name, station_file.name)
    )

    async with lazy_session() as session:
        task_repo = TaskRepo(session)
        station_repo = StationRepo(session)
        event_repo = EventRepo(session)
        detection_repo = DetectionRepo(session)

        for station_id, station in enumerate(station_table["station"]):
            await station_repo.create(
                network=station_table["network"][station_id],
                station=station,
                x=station_table["x"][station_id],
                y=station_table["y"][station_id],
                z=station_table["z"][station_id],
                task_id=task_id,
                commit=False
            )
        await session.commit()

        event_name_id = {}
        for event_name, payload in events.items():
            event = await event_repo.create(
                magnitude=payload[0],
                network=payload[1],
                x=payload[2],
                y=payload[3],
                z=payload[4],
                task_id=task_id,
                commit=True
            )
            event_name_id[event_name] = event.id

        for event_name, payload in detections.items():
            detection_list = payload[0]
            station_name = payload[1]
            station_id = (await station_repo.get(station=station_name, task_id=task_id)).id

            for detection in detection_list:
                await detection_repo.create(
                    phase=detection[0],
                    time=detection[1],
                    station_id=station_id,
                    event_id=event_name_id[event_name],
                    commit=False
                )
        await task_repo.update(id=task_id, state=TaskState.PENDING, step=TaskStep.SEISDATA, commit=False)
        await session.commit()

    os.remove(quake_file.name)
    os.remove(station_file.name)
