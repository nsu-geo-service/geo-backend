from .base import BaseView
from geo.models import schemas


class TomographyResponse(BaseView):
    content: schemas.Tomography
