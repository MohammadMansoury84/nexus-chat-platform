from uuid import UUID

from fastapi import WebSocket
from src.core.exceptions.WebSocketError import WebSocketConnectionError


class ConnectionManager:
    def __init__(self):

        self.active_connections: dict[UUID, WebSocket] = {}

    async def connect(self, user_id: UUID, web_socket: WebSocket) -> None:
        await web_socket.accept()
        self.active_connections[user_id] = web_socket

    def disconnect(self, user_id: UUID, web_socket: WebSocket) -> None:

        current_web_socket = self.active_connections.get(user_id)

        if not current_web_socket:
            return

        if current_web_socket == web_socket:
            self.active_connections.pop(user_id, None)

    def is_connected(self, user_id: UUID) -> bool:
        return bool(self.active_connections.get(user_id))

    async def send_personal(
        self,
        user_id: UUID,
        message: dict,
    ) -> None:

        try:
            web_socket = self._get_active_websocket(user_id)
            await web_socket.send_json(message)
        except WebSocketConnectionError:
            return
        except Exception:
            web_socket = self.active_connections.get(user_id)
            if web_socket:
                self.disconnect(user_id, web_socket)

    def _get_active_websocket(self, user_id: UUID) -> WebSocket:
        websocket = self.active_connections.get(user_id)
        if not websocket:
            raise WebSocketConnectionError("No active WebSocket connection found for user")
        return websocket
