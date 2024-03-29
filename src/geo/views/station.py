from .base import BaseView
from geo.models import schemas


class StationsResponse(BaseView):
    content: list[schemas.Station]
