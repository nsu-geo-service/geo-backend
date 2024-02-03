import logging
from datetime import timedelta

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError

from geo.config import load_env_config
from geo.controllers import (
    task_router, stats_router, geo_router,
)
from geo.controllers.proc import proc_router
from geo.exceptions import (
    APIError,
    handle_api_error,
    handle_404_error,
    handle_pydantic_error
)
from geo.lifespan import LifeSpan
from geo.services.storage import FileStorage
from geo.utils import custom_openapi
from geo.utils.http import HttpProcessor


class ApplicationFactory:

    @staticmethod
    def create_app() -> FastAPI:
        config = load_env_config(".env")
        logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)
        app = FastAPI(
            title="GeoService",
            debug=config.DEBUG,
            swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
            root_path="/api" if not config.DEBUG else "",
            docs_url="/api/docs" if config.DEBUG else "/docs",
            redoc_url="/api/redoc" if config.DEBUG else "/redoc",
        )
        app.openapi = lambda: custom_openapi(app)
        getattr(app, "state").config = config
        getattr(app, "state").storage = FileStorage("./storage")
        getattr(app, "state").http_client = HttpProcessor(
            timeout=timedelta(minutes=10).seconds,
            user_agent="aiohttp/3.7.4 (compatible; Geo/0.1.0)",
        )
        if not config.DEBUG:
            logging.getLogger("apscheduler").setLevel(logging.INFO)
            logging.getLogger("aiohttp").setLevel(logging.WARNING)
        lifespan = LifeSpan(app, config)
        app.add_event_handler("startup", lifespan.startup_handler)
        app.add_event_handler("shutdown", lifespan.shutdown_handler)

        logging.debug("Регистрация маршрутов API")
        api_router = APIRouter(prefix="/api/v1" if config.DEBUG else "")
        api_router.include_router(task_router)
        api_router.include_router(proc_router)
        api_router.include_router(geo_router)
        api_router.include_router(stats_router)
        app.include_router(api_router)

        logging.debug("Регистрация обработчиков исключений")
        app.add_exception_handler(APIError, handle_api_error)
        app.add_exception_handler(404, handle_404_error)
        app.add_exception_handler(RequestValidationError, handle_pydantic_error)

        logging.info("Приложение успешно создано")
        return app


application = ApplicationFactory.create_app()
