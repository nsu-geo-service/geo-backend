from .base import BaseView
from geo.models import schemas


class EventRowResponse(BaseView):
    content: schemas.EventRow
