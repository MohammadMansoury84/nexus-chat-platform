from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from src.api.dependencies.auth_service_dependency import get_current_user_id
from src.api.dependencies.message_service_dependency import get_message_service
from src.api.dependencies.realtime_publisher_dependency import get_realtime_publisher
from src.api.schemas.Request.message.send_message_request import SendMessageRequest
from src.api.schemas.Response.message.chat_message_response import ChatMessageResponse
from src.api.schemas.Response.message.send_message_response import SendMessageResponse
from src.api.schemas.Response.response import Response
from src.application.service.service_Interface.message_service import MessageService
from src.infrastructure.websocket.realtime_publisher import RealTimePublisher

message_router = APIRouter(
    prefix="/messages",
    tags=["Message"],
    dependencies=[Depends(get_current_user_id)],
)


@message_router.post(
    "/send_message",
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    request: SendMessageRequest,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
) -> Response[SendMessageResponse]:

    message = await message_service.send_message(
        sender_id=current_user_id, receiver_id=request.receiver_id, content=request.content
    )

    return Response[SendMessageResponse](
        data=SendMessageResponse(
            id=message.id,
            sender_username=message.sender_username,
            receiver_username=message.receiver_username,
            content=message.content,
            status=message.status,
        ),
        message="message send successfully",
    )


@message_router.get(
    "/chat/{user2_id}",
    response_model=Response[list[ChatMessageResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_chat(
    user2_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
) -> Response[list[ChatMessageResponse]]:

    messages = await message_service.get_chat(
        user1_id=current_user_id,
        user2_id=user2_id,
    )

    data = [
        ChatMessageResponse(
            sender_id=message.sender_id,
            username=message.username,
            content=message.content,
            status=message.status,
            timestamp=message.timestamp,
        )
        for message in messages
    ]

    return Response[list[ChatMessageResponse]](
        data=data,
        message=(
            "Chat history retrieved successfully."
            if messages
            else "You don't have any chat history with this user."
        ),
    )


@message_router.delete(
    "/chat/{user2_id}",
    response_model=Response[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_private_chat_history(
    user2_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
    realtime_publisher: Annotated[
        RealTimePublisher,
        Depends(get_realtime_publisher),
    ],
) -> Response[bool]:

    deleted = await message_service.delete_private_chat_history(
        user1_id=current_user_id,
        user2_id=user2_id,
    )

    await realtime_publisher.private_chat_deleted(
        user1_id=current_user_id, user2_id=user2_id, deleted_by=current_user_id
    )

    return Response[bool](
        data=deleted,
        message="Chat history deleted successfully",
    )
