from .base import BaseView
from geo.models import schemas


class SeisDataResponse(BaseView):
    content: schemas.SeisData
