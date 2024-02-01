from geo.models import tables
from geo.repositories.base import BaseRepository


class EventRepo(BaseRepository[tables.Event]):
    table = tables.Event
