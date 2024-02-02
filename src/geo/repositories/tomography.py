from geo.models import tables
from geo.repositories.base import BaseRepository


class TomographyRepo(BaseRepository[tables.Tomography]):
    table = tables.Tomography
