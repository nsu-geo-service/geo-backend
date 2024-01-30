from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from pydantic import BaseModel


class TaskState(Enum):
    PLAIN = 'PLAIN'
    IN_PROGRESS = 'IN_PROGRESS'
    PENDING = 'PENDING'
    DONE = 'DONE'
    FAILED = 'FAILED'


class TaskStep(Enum):
    STEP1 = 'STEP1'
    STEP2 = 'STEP2'


TaskID = NewType('TaskID', UUID)


class Task(BaseModel):
    id: TaskID
    state: TaskState
    step: TaskStep

    created_at: datetime

    class Config:
        from_attributes = True
