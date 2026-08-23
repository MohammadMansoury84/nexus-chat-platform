from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from src.api.schemas.WebSocket.websocket_request import WebSocketRequest
from src.infrastructure.websocket.connection_manager import ConnectionManager
from src.infrastructure.websocket.request_router import RequestRouter


class WebSocketHandler:
    def __init__(
        self, connection_manager: ConnectionManager, request_router: RequestRouter
    ) -> None:
        self._manager = connection_manager
        self._request_router = request_router

    async def handle(self, websocket: WebSocket, user_id: UUID) -> None:
        await self._manager.connect(user_id=user_id, web_socket=websocket)

        try:
            await self._listen(websocket=websocket, user_id=user_id)
        except WebSocketDisconnect:
            pass
        finally:
            self._manager.disconnect(user_id=user_id, web_socket=websocket)

    async def _listen(self, websocket: WebSocket, user_id: UUID) -> None:
        while True:
            data = await websocket.receive_json()
            await self._process_message(user_id=user_id, data=data)

    async def _process_message(self, user_id: UUID, data: dict) -> None:
        try:
            request = WebSocketRequest.model_validate(data)

            response_payload = await self._request_router.dispatch(
                user_id=user_id, request=request
            )

            if response_payload:
                await self._manager.send_personal(user_id=user_id, message=response_payload)

        except ValidationError as e:
            await self._manager.send_personal(
                user_id=user_id,
                message={
                    "event": "error",
                    "request_id": data.get("request_id"),
                    "data": {"details": e.errors(include_url=False)},
                },
            )
        except ValueError as e:
            await self._manager.send_personal(
                user_id=user_id,
                message={
                    "event": "error",
                    "request_id": data.get("request_id"),
                    "data": {"message": str(e)},
                },
            )
