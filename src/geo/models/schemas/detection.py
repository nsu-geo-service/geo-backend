from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Phase(Enum):
    P = 1
    S = 2


class Detection(BaseModel):
    id: UUID
    station_id: UUID
    phase: Phase
    time: float

    class Config:
        from_attributes = True
