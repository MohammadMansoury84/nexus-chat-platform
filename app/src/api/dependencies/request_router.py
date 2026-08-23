from typing import Annotated

from fastapi import Depends
from src.api.dependencies.request_handler_dependency import get_request_handler
from src.infrastructure.websocket.request_handler import RequestHandler
from src.infrastructure.websocket.request_router import RequestRouter
from src.infrastructure.websocket.websocket_router_config import create_websocket_router


def get_request_router(
    request_handler: Annotated[RequestHandler, Depends(get_request_handler)],
) -> RequestRouter:

    return create_websocket_router(request_handler)
