from fastapi import APIRouter, Depends
from fastapi import status as http_status

from geo.models.schemas import TaskID
from geo.services import ServiceFactory
from geo.services.di import get_services
from geo.views import SeisDataResponse, TomographyResponse, EventsResponse, StationsResponse

geo_router = APIRouter(prefix="/geo", tags=["Geo"])


@geo_router.get("/{task_id}/data", response_model=SeisDataResponse, status_code=http_status.HTTP_200_OK)
async def seisdata(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Данные для обработки (При создании таски)

    """
    return SeisDataResponse(content=await services.geo.seisdata(task_id=task_id))


@geo_router.get("/{task_id}/tomography", response_model=TomographyResponse, status_code=http_status.HTTP_200_OK)
async def tomography(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Данные для обработки (tomography)

    """
    return TomographyResponse(content=await services.geo.tomography(task_id=task_id))


@geo_router.get("/{task_id}/data/events", response_model=EventsResponse, status_code=http_status.HTTP_200_OK)
async def event_table(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Таблица событий

    """
    return EventsResponse(content=await services.geo.events(task_id))


@geo_router.get("/{task_id}/data/stations", response_model=StationsResponse, status_code=http_status.HTTP_200_OK)
async def station_table(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Таблица событий

    """
    return StationsResponse(content=await services.geo.stations(task_id))


@geo_router.get("/{task_id}/tomography/3d", status_code=http_status.HTTP_200_OK)
async def tomography_3d(
        task_id: TaskID,
        services: ServiceFactory = Depends(get_services)
):
    """
    3D модель томографии

    """
    ...
