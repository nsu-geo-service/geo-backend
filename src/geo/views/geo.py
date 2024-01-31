from .base import BaseView
from geo.models import schemas


class EventRowResponse(BaseView):
    content: schemas.EventRow


class StationRowResponse(BaseView):
    content: schemas.EventRow
