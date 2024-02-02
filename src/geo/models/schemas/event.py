from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    time: datetime
    magnitude: float
    network: str
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True
