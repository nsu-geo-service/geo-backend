from .base import BaseView
from geo.models import schemas


class EventsResponse(BaseView):
    content: list[schemas.Event]
