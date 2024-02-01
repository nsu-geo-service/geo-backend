import os
from dataclasses import dataclass
from logging import getLogger
from dotenv import load_dotenv

logger = getLogger(__name__)

DEBUG_ENV = "DEBUG"
FDSN_BASE_ENV = "FDSN_BASE"


class ConfigParseError(ValueError):
    pass


@dataclass
class Config:
    DEBUG: bool
    FDSN_BASE: str


def to_bool(value) -> bool:
    return str(value).strip().lower() in ("yes", "true", "t", "1")


def get_str_env(key: str, optional: bool = False) -> str:
    val = os.getenv(key)
    if not val and not optional:
        logger.error("%s is not set", key)
        raise ConfigParseError(f"{key} is not set")
    return val


def get_int_env(key: str, optional: bool = False) -> int:
    val = get_str_env(key, optional)
    try:
        return int(val)
    except ValueError:
        raise ConfigParseError("Value %s must be integer", val)


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
        FDSN_BASE=get_str_env(FDSN_BASE_ENV)
    )
