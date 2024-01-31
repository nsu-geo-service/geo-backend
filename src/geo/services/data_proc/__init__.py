import asyncio
import logging
import os
import pickle
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin
from uuid import UUID

import aiofiles
import numpy as np
import pandas as pd

from geo.models.schemas import DataProc, TaskState
from geo.services.data_proc.utils import (
    quake,
    generate_table,
    stations,
    relief_reader,
    change_coords_to_ST3D
)
from geo.services.storage import FileStorage
from geo.utils.http import HttpProcessor
from geo.utils.redis import RedisClient
from geo.utils.redis_queue import RedisQueue


async def fetch_from_base(http_client: HttpProcessor, url: str, params: dict = None):
    async with http_client as client:
        return await client.get(
            url=url,
            params=params
        )


async def worker(
        redis_client: RedisClient,
        redis_data_base: RedisClient,
        queue: RedisQueue,
        http_client: HttpProcessor,
        fdsn_base: str,
        storage: FileStorage,

):
    while True:
        await asyncio.sleep(3)
        task_id_str = await queue.dequeue()
        if not task_id_str:
            continue

        logging.info(f"[DataProc] Получена задача с id {task_id_str!r}")
        task_id = UUID(task_id_str)
        if not await redis_client.exists(str(task_id)):
            logging.warning(f"[DataProc] Задача с id {task_id!r} не существует, но существовала в очереди")
            continue

        raw_obj = await redis_data_base.get(f"{task_id_str}:data")
        if not raw_obj:
            logging.error(f"[DataProc] Данные задачи с id {task_id!r} не существуют, но существовали ранее")
            await redis_client.hset(str(task_id), {"state": TaskState.FAILED.value})
            continue

        data = DataProc.model_validate(pickle.loads(bytes.fromhex(raw_obj)))

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

        if not station_resp.is_success:
            logging.error(f"[DataProc] Ошибка при получении данных станций {station_resp.status_code}")
            await redis_client.hset(str(task_id), {"state": TaskState.FAILED.value})
            continue

        if not quake_resp.is_success:
            logging.error(f"[DataProc] Ошибка при получении данных событий {station_resp.status_code}")
            await redis_client.hset(str(task_id), {"state": TaskState.FAILED.value})
            continue

        quake_file = NamedTemporaryFile(delete_on_close=False)
        station_file = NamedTemporaryFile(delete_on_close=False)

        async with aiofiles.open(station_file.name, 'w') as file:
            await file.write(station_xml)

        async with aiofiles.open(quake_file.name, 'w') as file:
            await file.write(quake_xml)

        logging.info(f"[DataProc] Обработка данных")
        # CPU
        p_table, s_table = generate_table(pd.DataFrame(quake(quake_file.name)))
        station_list = stations(station_file.name)

        # Список станций station_info

        p_obs_time = np.asarray(p_table['Time'], dtype=np.float64)
        s_obs_time = np.asarray(s_table['Time'], dtype=np.float64)
        events_df = np.asarray(p_table['Event'], dtype=np.float64)
        stations_df = np.asarray(p_table['Station'], dtype=np.float64)

        relief_path = storage.abs_path("relief.dat")
        # # CPU
        # x_middle, y_middle, depth_topography, X_Y_Z_relief = relief_reader(relief_path, data.grid_size)
        #
        # LIM_COORD = X_Y_Z_relief[:3]
        # MAX_COORD = X_Y_Z_relief[3:]
        #
        # x_srcs, y_srcs, z_srcs = change_coords_to_ST3D(
        #     srcs[:, :1].flatten(),
        #     srcs[:, 1:2].flatten(),
        #     srcs[:, 2:3].flatten(),
        #     y_middle,
        #     x_middle
        # )
        # x_rcvrs, y_rcvrs, z_rcvrs = change_coords_to_ST3D(
        #     rsvrs[:, :1].flatten(),
        #     rsvrs[:, 1:2].flatten(),
        #     rsvrs[:, 2:3].flatten(),
        #     y_middle,
        #     x_middle
        # )
        #
        # X_Y_Z_srcs = np.column_stack((x_srcs, y_srcs, z_srcs))
        # X_Y_Z_rcvrs = np.column_stack((x_rcvrs, y_rcvrs, z_rcvrs))

        os.remove(quake_file.name)
        os.remove(station_file.name)
        print()
