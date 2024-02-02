from .base import BaseView
from geo.models import schemas


class EventsResponse(BaseView):
    content: schemas.Event
