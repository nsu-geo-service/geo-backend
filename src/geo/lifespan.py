import logging
from fastapi import FastAPI

from geo.utils.http import AiohttpClient

from geo.config import Config

class LifeSpan:

    def __init__(self, app: FastAPI, config: Config):
        self._app = app
        self._config = config

    async def startup_handler(self) -> None:
        logging.debug("Выполнение FastAPI startup event handler.")
        logging.info("FastAPI Успешно запущен.")

    async def shutdown_handler(self) -> None:
        logging.debug("Выполнение FastAPI shutdown event handler.")
