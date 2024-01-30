from fastapi.requests import Request

from geo.services import ServiceFactory


async def get_services(request: Request) -> ServiceFactory:
    global_scope = request.app.state
    local_scope = request.scope

    yield ServiceFactory(
        redis_client=global_scope.redis_client,
        data_queue=global_scope.data_queue,
        tomography_queue=global_scope.tomography_queue,
        redis_query_base=global_scope.redis_query_base,
        config=global_scope.config,
    )
