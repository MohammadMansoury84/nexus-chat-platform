from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from src.infrastructure.websocket.connection_manager import ConnectionManager


class WebSocketHandler:
    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.manager = connection_manager

    async def handle(self, websocket: WebSocket, user_id: UUID) -> None:
        await self.manager.connect(user_id=user_id, web_socket=websocket)

        try:
            await self._listen(websocket=websocket, user_id=user_id)
        except WebSocketDisconnect:
            pass
        finally:
            self.manager.disconnect(user_id=user_id, web_socket=websocket)

    async def _listen(self, websocket: WebSocket, user_id: UUID) -> None:

        while True:
            data = await websocket.receive_json()
            await self._process_message(user_id=user_id, data=data)

    async def _process_message(self, user_id: UUID, data: dict) -> None:

        pass
