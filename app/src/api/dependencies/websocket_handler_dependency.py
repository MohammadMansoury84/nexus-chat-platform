from typing import Annotated

from fastapi import Depends
from src.api.dependencies.websocket_dependency import get_connection_manager
from src.infrastructure.websocket.connection_manager import ConnectionManager
from src.infrastructure.websocket.WebSocketHandler import WebSocketHandler


def get_websocket_handler_dependency(
    connection_manager: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> WebSocketHandler:
    return WebSocketHandler(connection_manager=connection_manager)
