from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from pydantic import BaseModel, field_validator


class TaskState(Enum):
    ...


TaskID = NewType('TaskID', UUID)


class Task(BaseModel):
    id: TaskID
    state: TaskState

    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_must_be_valid(cls, value):
        if not is_valid_username(value):
            raise ValueError("Имя пользователя должно быть валидным")
        return value

    @field_validator('password')
    def password_must_be_valid(cls, value):
        if not is_valid_password(value):
            raise ValueError("Пароль должен быть валидным")
        return value
