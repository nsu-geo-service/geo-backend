from geo.models import tables
from geo.repositories.base import BaseRepository


class SeisDataRepo(BaseRepository[tables.SeisData]):
    table = tables.SeisData
