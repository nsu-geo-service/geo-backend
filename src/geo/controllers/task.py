from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from geo.services import ServiceFactory
from geo.services.dependencies import get_services

from geo.models import schemas
from geo.views.user import UserResponse

task_router = APIRouter(prefix="/task", tags=["Task"])


@task_router.get("", response_model=UserResponse, status_code=http_status.HTTP_200_OK)
async def task_list(services: ServiceFactory = Depends(get_services)):
    """
    Получить задачи

    """
    return UserResponse(content=await services.user.get_me())


@task_router.get("/{task_id}", response_model=UserResponse, status_code=http_status.HTTP_200_OK)
async def task_status(task_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить статус задачи по id

    """
    return UserResponse(content=await services.user.get_me())


@task_router.post("", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def new_task(data: schemas.UserUpdate, services: ServiceFactory = Depends(get_services)):
    """
    Создать новую задачу

    """
    await services.user.update_me(data)


# @task_router.put("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
# async def update_password(old_password: str, new_password: str, services: ServiceFactory = Depends(get_services)):
#     """
#     Обновить задачу по id
#
#     """
#     await services.user.update_password(old_password, new_password)


@task_router.delete("/{task_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить задачу по id

    """
    await services.user.delete_me(task_id)
