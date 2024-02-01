from .base import BaseView
from geo.models import schemas


class DataProcResponse(BaseView):
    content: schemas.SeisData


class TomographyProcResponse(BaseView):
    content: schemas.Tomography
