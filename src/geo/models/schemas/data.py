from datetime import datetime

from pydantic import BaseModel


class DataProc(BaseModel):
    start_time: datetime
    end_time: datetime
    all_origins: bool
    arrivals: bool
    network: str
