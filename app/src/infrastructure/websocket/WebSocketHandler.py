import asyncio
import time
import traceback
from uuid import UUID

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.WebSocket.websocket_error_code import WebSocketErrorCode
from src.api.schemas.WebSocket.websocket_request.web_socket_request import WebSocketRequest
from src.api.schemas.WebSocket.websocket_response.webSocket_error_data import (
    WebSocketErrorData,
)
from src.api.schemas.WebSocket.websocket_response.websocket_response import (
    WebSocketResponse,
)
from src.infrastructure.websocket.connection_manager import ConnectionManager
from src.infrastructure.websocket.request_router import RequestRouter
from src.infrastructure.websocket.websocket_error_mapper import (
    map_exception_to_websocket_error,
)


class WebSocketHandler:
    HEARTBEAT_INTERVAL = 20
    HEARTBEAT_TIMEOUT = 30

    def __init__(
        self,
        connection_manager: ConnectionManager,
        request_router: RequestRouter,
        session: AsyncSession,
    ) -> None:
        self._manager = connection_manager
        self._request_router = request_router
        self._db = session

    async def handle(
        self,
        websocket: WebSocket,
        user_id: UUID,
    ) -> None:

        await self._manager.connect(
            user_id=user_id,
            web_socket=websocket,
        )

        await self._broadcast_user_online(
            user_id=user_id,
        )

        last_pong = {
            "value": time.monotonic(),
        }

        heartbeat_task = asyncio.create_task(
            self._heartbeat(
                websocket=websocket,
                last_pong=last_pong,
            )
        )

        try:
            await self._listen(
                websocket=websocket,
                user_id=user_id,
                last_pong=last_pong,
            )

        except WebSocketDisconnect:
            pass

        finally:
            heartbeat_task.cancel()

            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

            self._manager.disconnect(
                user_id=user_id,
                web_socket=websocket,
            )

            await self._broadcast_user_offline(
                user_id=user_id,
            )

    async def _listen(
        self,
        websocket: WebSocket,
        user_id: UUID,
        last_pong: dict[str, float],
    ) -> None:

        while True:
            data = await websocket.receive_json()

            if data.get("action") == "pong":
                last_pong["value"] = time.monotonic()

                continue

            await self._process_message(
                user_id=user_id,
                data=data,
            )

    async def _heartbeat(
        self,
        websocket: WebSocket,
        last_pong: dict[str, float],
    ) -> None:

        while True:
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

            elapsed = time.monotonic() - last_pong["value"]

            if elapsed > self.HEARTBEAT_TIMEOUT:
                await websocket.close(
                    code=1001,
                    reason="Heartbeat timeout",
                )

                return

            await websocket.send_json(
                {
                    "event": "ping",
                    "request_id": None,
                    "data": {},
                }
            )

    async def _broadcast_user_online(
        self,
        user_id: UUID,
    ) -> None:

        recipients = self._manager.get_connected_user_ids() - {user_id}

        if not recipients:
            return

        await self._manager.broadcast_to_users(
            user_ids=recipients,
            message={
                "event": "user_online",
                "data": {
                    "user_id": str(user_id),
                },
            },
        )

    async def _broadcast_user_offline(
        self,
        user_id: UUID,
    ) -> None:

        recipients = self._manager.get_connected_user_ids()

        if not recipients:
            return

        await self._manager.broadcast_to_users(
            user_ids=recipients,
            message={
                "event": "user_offline",
                "data": {
                    "user_id": str(user_id),
                },
            },
        )

    async def _process_message(self, user_id: UUID, data: dict) -> None:
        request_id = data.get("request_id")

        try:
            request = WebSocketRequest.model_validate(data)

            result = await self._request_router.dispatch(user_id=user_id, request=request)
            await self._db.commit()
            if result:
                await self._send_response(user_id=user_id, result=result)

        except ValidationError as e:
            traceback.print_exc()
            await self._db.rollback()

            error_data = WebSocketErrorData(
                code=WebSocketErrorCode.INVALID_REQUEST,
                message="Data validation failed",
                details=e.errors(include_url=False),
            )

            await self._manager.send_personal(
                user_id=user_id,
                message={
                    "event": "error",
                    "data": error_data.model_dump(mode="json"),
                },
            )

        except Exception as e:
            traceback.print_exc()
            await self._db.rollback()

            error_code = map_exception_to_websocket_error(e)

            if isinstance(e, HTTPException):
                message = e.detail
            elif error_code == WebSocketErrorCode.INTERNAL_SERVER_ERROR:
                message = "An unexpected internal server error occurred."
            else:
                message = str(e)

            error_data = WebSocketErrorData(code=error_code, message=message)

            await self._manager.send_personal(
                user_id=user_id,
                message={
                    "event": "error",
                    "request_id": request_id,
                    "data": error_data.model_dump(mode="json"),
                },
            )

    async def _send_response(self, user_id: UUID, result: dict) -> None:
        response: WebSocketResponse = result["response"]
        payload = response.model_dump(mode="json")

        await self._manager.send_personal(user_id=user_id, message=payload)

        broadcast_payload = payload.copy()
        broadcast_payload["request_id"] = None

        match response.event:
            case "private_message":
                receiver_id = result.get("receiver_id")
                if receiver_id and receiver_id != user_id:
                    await self._manager.send_personal(
                        user_id=receiver_id,
                        message=broadcast_payload,
                    )
            case "message_read":
                sender_of_messages = result.get("receiver_id")
                if sender_of_messages and sender_of_messages != user_id:
                    await self._manager.send_personal(
                        user_id=sender_of_messages,
                        message=broadcast_payload,
                    )

            case "group_message":
                member_ids = result.get("member_ids", [])
                other_members = [
                    member_id for member_id in member_ids if member_id != user_id
                ]
                if other_members:
                    await self._manager.broadcast_to_users(
                        user_ids=other_members,
                        message=broadcast_payload,
                    )

            case _:
                pass
