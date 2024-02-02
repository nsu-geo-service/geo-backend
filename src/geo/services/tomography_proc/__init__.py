import logging
import os
import subprocess
from tempfile import NamedTemporaryFile

import aiofiles
import h5py
import numpy as np
from aiomultiprocess import Worker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from geo.models.schemas import TaskState, TaskStep
from geo.repositories import TaskRepo
from geo.repositories.detection import DetectionRepo
from geo.repositories.event import EventRepo
from geo.repositories.station import StationRepo
from geo.repositories.tomography import TomographyRepo
from geo.services.storage import FileStorage
from geo.services.tomography_proc.utils import change_coords_to_ST3D, relief_read, create_start_model
from geo.utils.queue import Queue


async def cpu_worker(executable: str, input_file: str, output_file: str):
    logging.info(f"[TomographyProc] Запуск процесса {input_file!r} -> {output_file!r}")
    is_ok = False
    try:
        subprocess.run(
            [executable, input_file, output_file],
            check=True,
        )
        is_ok = True
    except subprocess.CalledProcessError as error:
        logging.error(error)
    logging.info(f"[TomographyProc] Процесс {input_file!r} завершен")
    return is_ok


async def worker(queue: Queue, lazy_session: async_sessionmaker[AsyncSession], storage: FileStorage, executable: str):
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

    relief_path = storage.abs_path("relief.dat")
    x_middle, y_middle, depth_topography, X_Y_Z_relief = relief_read(relief_path, data.grid_size)

    LIM_COORD = X_Y_Z_relief[:3]
    MAX_COORD = X_Y_Z_relief[3:]

    LIM_COORD[2] = -1
    MAX_COORD[2] = 60

    async with lazy_session() as session:
        event_repo = EventRepo(session)
        station_repo = StationRepo(session)
        detection_repo = DetectionRepo(session)
        events = await event_repo.get_all(
            task_id=task_id
        )
        stations = await station_repo.get_all(
            task_id=task_id
        )
        detections = await detection_repo.get_all_by_task(
            task_id=task_id
        )

    events_x = [event.x for event in events]
    events_y = [event.y for event in events]
    events_z = [event.z for event in events]

    stations_x = [station.x for station in stations]
    stations_y = [station.y for station in stations]
    stations_z = [station.z for station in stations]

    p_times = [detection.time for detection in detections if detection.phase == "P"]
    s_times = [detection.time for detection in detections if detection.phase == "S"]

    p_obs_time = np.asarray(p_times, dtype=np.float64)
    s_obs_time = np.asarray(s_times, dtype=np.float64)
    events_df = np.asarray([i for i in range(len(events))], dtype=np.float64)
    stations_df = np.asarray([el.station for el in stations], dtype=np.float64)

    x_event, y_event, z_event = change_coords_to_ST3D(
        FI=np.array(events_x),
        TET=np.array(events_y),
        h=np.array(events_z),
        fi0=y_middle,
        tet0=x_middle
    )
    x_station, y_station, z_station = change_coords_to_ST3D(
        FI=np.array(stations_x),
        TET=np.array(stations_y),
        h=np.array(stations_z),
        fi0=y_middle,
        tet0=x_middle
    )

    X_Y_Z_srcs = np.column_stack((x_event, y_event, z_event))
    X_Y_Z_rcvrs = np.column_stack((x_station, y_station, z_station))

    input_file = NamedTemporaryFile(delete_on_close=False)
    with h5py.File(input_file.name, "w") as file:
        hps_st3d_group = file.create_group("HPS_ST3D")
        group_input = hps_st3d_group.create_group("Input")
        group_input.attrs["IterMax"] = np.array([data.iter_max], dtype=np.int64)
        group_input.attrs["IterResidLimits"] = np.full(np.int64(data.iter_max), 1.5, dtype=np.float64)
        group_input.attrs["LinSysLSQRIterMax"] = np.array([data.lin_sys_LSQR_iter_max], dtype=np.int64)
        group_input.attrs["ParamType"] = np.array([2], dtype=np.uint8)
        group_input.attrs["SrcsPsvRelocLimit"] = np.array([40, 40, 40], dtype=np.float64)
        group_input.attrs["TomoGridRotAngles"] = np.array([0, 22.5, 45, 67.5], dtype=np.float64)
        group_input.attrs["TomoGridStep"] = np.array(data.grid_step, dtype=np.float64)

        group_input.attrs["TomoMatDampingP"] = np.asarray([data.mat_damping_P], dtype=np.float64)
        group_input.attrs["TomoMatDampingP4V"] = np.asarray([data.mat_damping_P4V], dtype=np.float64)
        group_input.attrs["TomoMatDampingS"] = np.asarray([data.mat_damping_S], dtype=np.float64)
        group_input.attrs["TomoMatDampingS4V"] = np.asarray([data.mat_damping_S4V], dtype=np.float64)
        group_input.attrs["TomoMatSmoothHP"] = np.asarray([data.mat_damping_HP], dtype=np.float64)
        group_input.attrs["TomoMatSmoothHP4V"] = np.asarray([data.mat_damping_HP4V], dtype=np.float64)
        group_input.attrs["TomoMatSmoothHS"] = np.asarray([data.mat_damping_HS], dtype=np.float64)
        group_input.attrs["TomoMatSmoothHS4V"] = np.asarray([data.mat_damping_HS4V], dtype=np.float64)
        group_input.attrs["TomoMatSmoothVP"] = np.asarray([data.mat_damping_VP], dtype=np.float64)
        group_input.attrs["TomoMatSmoothVP4V"] = np.asarray([data.mat_damping_VP4V], dtype=np.float64)
        group_input.attrs["TomoMatSmoothVS"] = np.asarray([data.mat_damping_VS], dtype=np.float64)
        group_input.attrs["TomoMatSmoothVS4V"] = np.asarray([data.mat_damping_VS4V], dtype=np.float64)

        # Атрибуты "VLimitsP" и "VLimitsS"
        group_input.attrs["VLimitsP"] = np.array([0.1, 10], dtype=np.float64)
        group_input.attrs["VLimitsS"] = np.array([0.1, 10], dtype=np.float64)

        # Группа "RaysPsv"
        group_rays_psv = group_input.create_group("RaysPsv")

        # Датасет "P"
        group_rays_psv_p = group_rays_psv.create_group("P")
        group_rays_psv_p.create_dataset("TObs", shape=len(p_obs_time), data=p_obs_time, dtype=np.float64)

        # Датасет "Rcvs"
        group_rays_psv.create_dataset("Rcvs", shape=len(stations_df), data=stations_df, dtype=np.int64)

        # Датасет "S"
        group_rays_psv_s = group_rays_psv.create_group("S")
        group_rays_psv_s.create_dataset("TObs", shape=len(s_obs_time), data=s_obs_time, dtype=np.float64)

        # Датасет "Srcs"
        group_rays_psv.create_dataset("Srcs", shape=len(events_df), data=events_df, dtype=np.int64)

        # Группа "Rcvs"
        group_rcvs = group_input.create_group("Rcvs")

        # Датасет "Coords"
        group_rcvs.create_dataset("Coords", shape=(X_Y_Z_rcvrs.shape[0], 3), data=X_Y_Z_rcvrs, dtype=np.float64)

        # Группа "SrcsPsv"
        group_srcs_psv = group_input.create_group("SrcsPsv")

        # Датасет "Coords"
        group_srcs_psv.create_dataset("Coords", shape=(X_Y_Z_srcs.shape[0], 3), data=X_Y_Z_srcs, dtype=np.float64)

        # Датасет "Topography"
        group_input.create_dataset("Topography", shape=depth_topography.shape, data=depth_topography, dtype=np.float64)

        # Группа "VGrid"
        group_vgrid = group_input.create_group("VGrid")

        # Атрибуты "CoordLimHigh", "CoordLimLow", "GridSize", "GridStep"
        group_vgrid.attrs["CoordLimHigh"] = np.asarray(MAX_COORD, dtype=np.float64)
        group_vgrid.attrs["CoordLimLow"] = np.asarray(LIM_COORD, dtype=np.float64)
        group_vgrid.attrs["GridSize"] = np.asarray(data.grid_size, dtype=np.int64)
        Grid_Step = np.abs(MAX_COORD - LIM_COORD)
        group_vgrid.attrs["GridStep"] = np.array([
            (Grid_Step[0]) / (data.grid_size[0] - 1),
            (Grid_Step[1]) / (data.grid_size[1] - 1),
            (Grid_Step[2]) / (data.grid_size[2] - 1)
        ], dtype=np.float64)

        Vp_st, Vs_st = create_start_model(data.base_model, data.grid_size)

        # Датасеты "VP" и "VS"
        group_vgrid.create_dataset("VP", shape=Vp_st.shape, data=Vp_st, dtype='float64')
        group_vgrid.create_dataset("VS", shape=Vs_st.shape, data=Vs_st, dtype='float64')
    await storage.save(f"{task_id}/input.h5", input_file.read(), "wb")
    os.remove(input_file.name)

    # Запуск процесса
    is_ok = await Worker(
        target=cpu_worker,
        args=(executable, storage.abs_path(f"{task_id}/input.h5"), storage.abs_path(f"{task_id}/output.h5"))
    )
    async with lazy_session() as session:
        task_repo = TaskRepo(session)

        if is_ok:
            await task_repo.update(
                id=task_id,
                state=TaskState.DONE,
                step=TaskStep.TOMOGRAPHY
            )
        else:
            await task_repo.update(
                id=task_id,
                state=TaskState.FAILED
            )
