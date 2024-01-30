
from fastapi import APIRouter, Depends
from fastapi import status as http_status

from geo.models.schemas import TaskID
from geo.services import ServiceFactory
from geo.services.di import get_services

from geo.models import schemas
from geo.views.task import TasksResponse, TaskResponse

task_router = APIRouter(prefix="/task", tags=["Task"])


@task_router.get("", response_model=TasksResponse, status_code=http_status.HTTP_200_OK)
async def task_list(services: ServiceFactory = Depends(get_services)):
    """
    Получить задачи

    """
    return TasksResponse(content=await services.task.list())


@task_router.get("/{task_id}", response_model=TaskResponse, status_code=http_status.HTTP_200_OK)
async def task(task_id: TaskID, services: ServiceFactory = Depends(get_services)):
    """
    Получить задачу по id

    """
    return TaskResponse(content=await services.task.get_task(task_id))


@task_router.post("", response_model=TaskResponse, status_code=http_status.HTTP_200_OK)
async def new_task(data: schemas.TaskCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать новую задачу

    """
    return TaskResponse(content=await services.task.new_task(data))


@task_router.delete("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: TaskID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить задачу по id

    """
    await services.task.delete_task(task_id)

