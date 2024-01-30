import os
from dataclasses import dataclass
from logging import getLogger
from dotenv import load_dotenv

logger = getLogger(__name__)

DEBUG_ENV = "DEBUG"
POSTGRES_HOST_ENV = "POSTGRES_HOST"
POSTGRES_PORT_ENV = "POSTGRES_PORT"
POSTGRES_USERNAME_ENV = "POSTGRES_USERNAME"
POSTGRES_PASSWORD_ENV = "POSTGRES_PASSWORD"
POSTGRES_DATABASE_ENV = "POSTGRES_DATABASE"

JWT_SECRET_KEY_ENV = "JWT_SECRET_KEY"


class ConfigParseError(ValueError):
    pass


@dataclass
class PostgresConfig:
    DATABASE: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int


@dataclass
class DbConfig:
    POSTGRESQL: PostgresConfig


@dataclass
class JWTConfig:
    SECRET_KEY: str


@dataclass
class S3Config:
    BUCKET: str
    ENDPOINT_URL: str
    PUBLIC_ENDPOINT_URL: str
    REGION: str
    ACCESS_KEY_ID: str
    ACCESS_KEY: str


@dataclass
class Config:
    DEBUG: bool
    DB: DbConfig
    JWT: JWTConfig
    S3: S3Config


def to_bool(value) -> bool:
    return str(value).strip().lower() in ("yes", "true", "t", "1")


def get_str_env(key: str, optional: bool = False) -> str:
    val = os.getenv(key)
    if not val and not optional:
        logger.error("%s is not set", key)
        raise ConfigParseError(f"{key} is not set")
    return val


def load_env_config(env_file: str | os.PathLike = None) -> Config:
    if not env_file:
        env_file = ".env"

    if os.path.exists(env_file):
        logger.info(f"Loading env from {env_file!r}")

        load_dotenv(env_file)
    else:
        logger.info("Loading env from os.environ")

    return Config(
        DEBUG=to_bool(get_str_env(DEBUG_ENV)),
        DB=DbConfig(
            POSTGRESQL=PostgresConfig(
                HOST=get_str_env(POSTGRES_HOST_ENV),
                PORT=int(get_str_env(POSTGRES_PORT_ENV)),
                USERNAME=get_str_env(POSTGRES_USERNAME_ENV),
                PASSWORD=get_str_env(POSTGRES_PASSWORD_ENV),
                DATABASE=get_str_env(POSTGRES_DATABASE_ENV),
            )
        ),
        JWT=JWTConfig(
            SECRET_KEY=get_str_env(JWT_SECRET_KEY_ENV),
        ),
        S3=S3Config(
            BUCKET=get_str_env("S3_BUCKET"),
            ENDPOINT_URL=get_str_env("S3_ENDPOINT_URL"),
            PUBLIC_ENDPOINT_URL=get_str_env("S3_PUBLIC_ENDPOINT_URL", optional=True),
            REGION=get_str_env("S3_REGION"),
            ACCESS_KEY_ID=get_str_env("S3_ACCESS_KEY_ID"),
            ACCESS_KEY=get_str_env("S3_ACCESS_KEY"),
        )
    )
