from datetime import datetime

from pydantic import BaseModel


class Station(BaseModel):
    network: str
    station: str
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True
