from fastapi.requests import Request

from geo.services import ServiceFactory


async def get_services(request: Request) -> ServiceFactory:
    global_scope = request.app.state
    local_scope = request.scope

    yield ServiceFactory(
        data_queue=global_scope.data_queue,
        tomography_queue=global_scope.tomography_queue,
        lazy_session=global_scope.db_session,
        config=global_scope.config,
        storage=global_scope.storage
    )
