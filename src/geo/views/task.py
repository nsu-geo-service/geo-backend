from .base import BaseView
from geo.models import schemas


class TaskResponse(BaseView):
    content: schemas.Task


class TasksResponse(BaseView):
    content: list[schemas.Task]


class TaskCountResponse(BaseView):
    content: int
