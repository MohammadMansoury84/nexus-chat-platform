from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends,status
from src.api.schemas.Response.message.chat_message_response import ChatMessageResponse
from src.api.schemas.Response.response import Response
from src.application.service.service_Interface.message_service import MessageService
from src.api.schemas.Request.message.send_message_request import SendMessageRequest
from src.api.schemas.Response.message.send_message_response import SendMessageResponse
from src.api.dependencies.auth_service_dependency import get_current_user_id
from src.api.dependencies.message_service_dependency import get_message_service

message_router = APIRouter(
    prefix="/messages",
    tags=["Message"],
    dependencies=[Depends(get_current_user_id)],
)

@message_router.post(
    "/send_message",
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    request: SendMessageRequest,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
    )->Response[SendMessageResponse]:

    message=message_service.send_message(
        sender_id=current_user_id,
        receiver_id=request.receiver_id,
        content=request.content
        )

    return Response[SendMessageResponse](
        data=SendMessageResponse(
            id=message.id,
            sender_username=message.sender_username,
            receiver_username=message.receiver_username,
            content=message.content,
            status=message.status
        ),
        message="message send successfully"
    )

@message_router.get(
    "/chat/{user2_id}",
    response_model=Response[list[ChatMessageResponse]],
    status_code=status.HTTP_200_OK,
)
def get_chat(
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

    messages = message_service.get_chat(
        user1_id=current_user_id,
        user2_id=user2_id,
    )

    data = [
        ChatMessageResponse(
            sender_id=message.sender_id,
            username=message.username,
            content=message.content,
            status=message.status,
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
def delete_private_chat_history(
    user2_id: UUID,
    current_user_id: Annotated[
        UUID,
        Depends(get_current_user_id),
    ],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
) -> Response[bool]:

    deleted = message_service.delete_private_chat_history(
        user1_id=current_user_id,
        user2_id=user2_id,
    )

    return Response[bool](
        data=deleted,
        message="Chat history deleted successfully",
    )