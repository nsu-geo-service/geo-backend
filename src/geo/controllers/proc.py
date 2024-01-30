from fastapi import APIRouter, Depends
from fastapi import status as http_status

from geo.models.schemas import TaskID
from geo.models.schemas.data import DataProc
from geo.models.schemas.tomography import TomographyProc
from geo.services import ServiceFactory
from geo.services.di import get_services

proc_router = APIRouter(prefix="/proc", tags=["Process"])


@proc_router.post("/data/{task_id}", response_model=None, status_code=http_status.HTTP_202_ACCEPTED)
async def data_proc(
        task_id: TaskID,
        data: DataProc,
        services: ServiceFactory = Depends(get_services)
):
    """
    Запуск процесса обработки данных

    """
    await services.geo.data_proc(task_id=task_id, data=data)


@proc_router.post("/tomography/{task_id}", response_model=None, status_code=http_status.HTTP_202_ACCEPTED)
async def tomography_proc(
        task_id: TaskID,
        data: TomographyProc,
        services: ServiceFactory = Depends(get_services)
):
    """
    Запуск процесса томографии

    """
    await services.geo.tomography_proc(
        task_id=task_id,
        data=data,
    )
