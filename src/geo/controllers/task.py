from fastapi import APIRouter, Depends
from fastapi import status as http_status

from geo.models.schemas import TaskID
from geo.services import ServiceFactory
from geo.services.di import get_services

from geo.views.task import TasksResponse, TaskResponse, TaskCountResponse

task_router = APIRouter(prefix="/task", tags=["Task"])


@task_router.get("", response_model=TasksResponse, status_code=http_status.HTTP_200_OK)
async def task_list(
        page: int = 1,
        per_page: int = 10,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить список задач

    """
    return TasksResponse(content=await services.task.list(page, per_page))


@task_router.get("/count", response_model=TaskCountResponse, status_code=http_status.HTTP_200_OK)
async def task_count(services: ServiceFactory = Depends(get_services)):
    """
    Получить количество задач

    """
    return TaskCountResponse(content=await services.task.count())


@task_router.get("/{task_id}", response_model=TaskResponse, status_code=http_status.HTTP_200_OK)
async def task(task_id: TaskID, services: ServiceFactory = Depends(get_services)):
    """
    Получить задачу по id

    """
    return TaskResponse(content=await services.task.get_task(task_id))


@task_router.post("", response_model=TaskResponse, status_code=http_status.HTTP_200_OK)
async def new_task(services: ServiceFactory = Depends(get_services)):
    """
    Создать новую задачу

    """
    return TaskResponse(content=await services.task.new_task())


@task_router.delete("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: TaskID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить задачу по id

    """
    await services.task.delete_task(task_id)
