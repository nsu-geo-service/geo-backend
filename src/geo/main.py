import logging
from datetime import timedelta

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError

from geo.config import load_env_config
from geo.controllers import (
    task_router, stats_router,
)
from geo.exceptions import (
    APIError,
    handle_api_error,
    handle_404_error,
    handle_pydantic_error
)
from geo.lifespan import LifeSpan
from geo.utils import custom_openapi
from geo.utils.http import AiohttpClient


class ApplicationFactory:

    @staticmethod
    def create_app() -> FastAPI:
        config = load_env_config(".env")
        logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)
        app = FastAPI(
            title="GeoService",
            debug=config.DEBUG,
            swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
            docs_url="/api/v1/docs",
            redoc_url="/api/v1/redoc",
        )
        app.openapi = lambda: custom_openapi(app)
        getattr(app, "state").config = config
        getattr(app, "state").http_client = AiohttpClient(
            timeout=timedelta(seconds=2),
            limit_per_host=100,
            agent=f"aiohttp/3.9.3 (compatible; Geo/0.1.0)",
        )

        lifespan = LifeSpan(app, config)
        app.add_event_handler("startup", lifespan.startup_handler)
        app.add_event_handler("shutdown", lifespan.shutdown_handler)

        logging.debug("Регистрация маршрутов API")
        api_router = APIRouter(prefix="/api/v1")
        api_router.include_router(task_router)
        api_router.include_router(stats_router)
        app.include_router(api_router)

        logging.debug("Регистрация обработчиков исключений")
        app.add_exception_handler(APIError, handle_api_error)
        app.add_exception_handler(404, handle_404_error)
        app.add_exception_handler(RequestValidationError, handle_pydantic_error)

        logging.info("Приложение успешно создано")
        return app


application = ApplicationFactory.create_app()
