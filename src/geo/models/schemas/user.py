import re
from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from pydantic import BaseModel, field_validator

from .role import RoleMedium, RoleSmall, Role


class UserState(Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


def is_valid_username(username: str) -> bool:
    pattern = r"^(?=.{4,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"
    return re.match(pattern, username) is not None


def is_valid_password(password: str) -> bool:
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,32}$"
    return re.match(pattern, password) is not None


UserID = NewType('UserID', UUID)


class User(BaseModel):
    id: UserID
    username: str
    role: Role
    state: UserState

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class UserMedium(BaseModel):
    id: UserID
    username: str
    role: RoleMedium
    state: UserState

    created_at: datetime


class UserSmall(BaseModel):
    id: UserID
    username: str
    role: RoleSmall
    state: UserState

    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
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


class UserAuth(BaseModel):
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


class UserUpdate(BaseModel):
    username: str = None

    @field_validator('username')
    def username_must_be_valid(cls, value):
        if value and not is_valid_username(value):
            raise ValueError("Имя пользователя должно быть валидным")
        return value


class UserUpdateByAdmin(UserUpdate):
    role_id: UserID = None
    state: UserState = None
