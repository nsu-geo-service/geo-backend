from fastapi import APIRouter, Depends
from fastapi import status as http_status

from geo.models.schemas import TaskID
from geo.services import ServiceFactory
from geo.services.di import get_services
from geo.views.geo import EventRowResponse
from geo.views.proc import DataProcResponse, TomographyProcResponse

geo_router = APIRouter(prefix="/geo", tags=["Geo"])


@geo_router.get("/{task_id}/data", response_model=DataProcResponse, status_code=http_status.HTTP_200_OK)
async def data(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Данные для обработки (При создании таски)

    """
    return DataProcResponse(content=await services.geo.data(task_id=task_id))


@geo_router.get("/{task_id}/tomography", response_model=TomographyProcResponse, status_code=http_status.HTTP_200_OK)
async def tomography(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Данные для обработки (tomography)

    """
    return TomographyProcResponse(content=await services.geo.data(task_id=task_id))


@geo_router.get("/{task_id}/data/events", response_model=EventRowResponse, status_code=http_status.HTTP_200_OK)
async def event_table(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Таблица событий

    """
    ...


@geo_router.get("/{task_id}/data/station", response_model=EventRowResponse, status_code=http_status.HTTP_200_OK)
async def station_table(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Таблица событий

    """
    ...



@geo_router.get("/{task_id}/tomography/3d", response_model=EventRowResponse, status_code=http_status.HTTP_200_OK)
async def tomography_3d(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    3D модель томографии

    """
    ...
