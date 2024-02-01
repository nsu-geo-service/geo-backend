from geo.models import tables
from geo.repositories.base import BaseRepository


class DetectionRepo(BaseRepository[tables.Detection]):
    table = tables.Detection
