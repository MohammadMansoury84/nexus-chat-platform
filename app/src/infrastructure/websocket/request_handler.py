from uuid import UUID

from src.api.schemas.WebSocket.websocket_request.message_read_data import MessageReadData
from src.api.schemas.WebSocket.websocket_request.send_group_message_data import (
    SendGroupMessageData,
)
from src.api.schemas.WebSocket.websocket_request.send_private_message_data import (
    SendPrivateMessageData,
)
from src.api.schemas.WebSocket.websocket_response.websocket_response import (
    WebSocketResponse,
)
from src.application.service.service_Interface.group_service import GroupService
from src.application.service.service_Interface.message_service import MessageService


class RequestHandler:
    def __init__(
        self,
        message_service: MessageService,
        group_service: GroupService,
    ) -> None:
        self._message_service = message_service
        self._group_service = group_service

    async def handle_send_private_message(
        self,
        user_id: UUID,
        data: dict,
    ) -> dict:

        payload = SendPrivateMessageData.model_validate(data)

        message = await self._message_service.send_message(
            sender_id=user_id,
            receiver_id=payload.receiver_id,
            content=payload.content,
        )

        response = WebSocketResponse(
            event="private_message",
            data={
                "message_id": str(message.id),
                "sender_id": str(user_id),
                "receiver_id": str(payload.receiver_id),
                "content": payload.content,
            },
        )

        return {
            "response": response,
            "receiver_id": payload.receiver_id,
        }

    async def handle_send_group_message(
        self,
        user_id: UUID,
        data: dict,
    ) -> dict:
        payload = SendGroupMessageData.model_validate(data)

        message = await self._group_service.send_message_to_group(
            group_id=payload.group_id,
            sender_id=user_id,
            content=payload.content,
        )

        members = await self._group_service.show_group_member(
            user_id=user_id,
            group_id=payload.group_id,
        )
        member_ids = [member.id for member in members]

        response = WebSocketResponse(
            event="group_message",
            data={
                "message_id": str(message.id),
                "group_id": str(payload.group_id),
                "sender_id": str(user_id),
                "content": payload.content,
            },
        )

        return {
            "response": response,
            "member_ids": member_ids,
        }

    async def handel_message_read(
        self,
        user_id: UUID,
        data: dict,
    ) -> dict:
        payload = MessageReadData.model_validate(data)
        read_message_ids = await self._message_service.mark_chat_as_read(
            reader_id=user_id,
            chat_partner_id=payload.chat_partner_id,
        )

        response = WebSocketResponse(
            event="message_read",
            data={
                "reader_id": str(user_id),
                "chat_partner_id": str(payload.chat_partner_id),
                "read_message_ids": [str(message_id) for message_id in read_message_ids],
            },
        )

        return {
            "response": response,
            "receiver_id": payload.chat_partner_id,
        }
