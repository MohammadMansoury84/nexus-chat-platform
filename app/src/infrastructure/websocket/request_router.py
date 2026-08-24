from collections.abc import Awaitable, Callable
from uuid import UUID

from src.api.schemas.WebSocket.websocket_action import WebSocketAction
from src.api.schemas.WebSocket.websocket_request.web_socket_request import WebSocketRequest

WebSocketHandlerFunc = Callable[[UUID, UUID | None, dict], Awaitable[dict]]


class RequestRouter:
    def __init__(self) -> None:
        self._routes: dict[WebSocketAction, WebSocketHandlerFunc] = {}

    def register_route(
        self,
        action: WebSocketAction,
        handler: WebSocketHandlerFunc,
    ) -> None:
        self._routes[action] = handler

    async def dispatch(self, user_id: UUID, request: WebSocketRequest) -> dict:

        handler = self._routes.get(request.action)

        if not handler:
            raise ValueError("No handler registered for action")

        return await handler(user_id, request.data)
