from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from pydantic import BaseModel, field_validator


class TaskState(Enum):
    PLAIN = 'plain'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'
    DONE = 'done'
    FAILED = 'failed'


TaskID = NewType('TaskID', UUID)


class Task(BaseModel):
    id: TaskID
    state: TaskState

    created_at: datetime

    class Config:
        from_attributes = True
