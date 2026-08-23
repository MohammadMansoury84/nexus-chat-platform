from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from src.api.dependencies.websocket_dependency import (
    get_current_websocket_user_id,
)
from src.api.dependencies.websocket_handler_dependency import (
    get_websocket_handler_dependency,
)
from src.infrastructure.websocket import WebSocketHandler

websocket_router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"],
)


@websocket_router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_websocket_user_id),
    ],
    websocket_handler: Annotated[
        WebSocketHandler,
        Depends(get_websocket_handler_dependency),
    ],
) -> None:

    await websocket_handler.handle(websocket=websocket, user_id=current_user_id)
