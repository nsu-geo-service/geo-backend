from datetime import datetime

from pydantic import BaseModel


class DataProc(BaseModel):
    start_time: datetime
    end_time: datetime
    network: str
    min_latitude: int | float | None = None
    max_latitude: int | float | None = None
    min_longitude: int | float | None = None
    max_longitude: int | float | None = None


class EventRow(BaseModel):
    network: str
    station: str
    x: float | int
    y: float | int
    z: float | int
    event: int


class StationRow(BaseModel):
    network: str
    station: str
    x: float | int
    y: float | int
    z: float | int
