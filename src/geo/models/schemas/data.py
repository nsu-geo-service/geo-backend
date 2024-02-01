from datetime import datetime

from pydantic import BaseModel


class SeisData(BaseModel):
    start_time: datetime
    end_time: datetime
    network: str
    min_latitude: float | None = None
    max_latitude: float | None = None
    min_longitude: float | None = None
    max_longitude: float | None = None

    class Config:
        from_attributes = True


class EventRow(BaseModel):
    network: str
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True


class StationRow(BaseModel):
    network: str
    station: str
    x: float
    y: float
    z: float

    class Config:
        from_attributes = True
