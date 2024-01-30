from fastapi.requests import Request

from geo.services import ServiceFactory


async def get_services(request: Request) -> ServiceFactory:
    global_scope = request.app.state
    local_scope = request.scope

    yield ServiceFactory(
        redis_queue=global_scope.redis_queue,
        config=global_scope.config,
    )
