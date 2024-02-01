from geo.models import tables
from geo.repositories.base import BaseRepository


class StationRepo(BaseRepository[tables.Station]):
    table = tables.Station
