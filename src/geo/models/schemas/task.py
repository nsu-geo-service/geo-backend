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
    DATA = 'DATA'
    TOMOGRAPHY = 'TOMOGRAPHY'


TaskID = NewType('TaskID', UUID)


class Task(BaseModel):
    id: TaskID
    state: TaskState
    step: TaskStep | None

    created_at: datetime
    completed_in: datetime | None
