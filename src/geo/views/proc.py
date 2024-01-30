from .base import BaseView
from geo.models import schemas


class DataProcResponse(BaseView):
    content: schemas.DataProc


class TomographyProcResponse(BaseView):
    content: schemas.TomographyProc
