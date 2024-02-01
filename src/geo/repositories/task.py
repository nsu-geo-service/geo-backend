from geo.models import tables
from geo.repositories.base import BaseRepository


class TaskRepo(BaseRepository[tables.Task]):
    table = tables.Task
