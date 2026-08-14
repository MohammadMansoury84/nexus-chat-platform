from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends,status
from src.api.schemas.Response.response import Response
from src.application.service.service_Interface.message_service import MessageService
from src.api.schemas.Request.send_message_request import SendMessageRequest
from src.api.schemas.Response.send_message_response import SendMessageResponse
from src.api.dependencies.auth_service_dependency import get_current_user_id
from src.api.dependencies.message_service_dependency import get_message_service

message_router = APIRouter(
    prefix="/message",
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