from typing import Annotated

from fastapi import Depends
from src.api.dependencies.group_service_dependency import get_group_service
from src.api.dependencies.message_service_dependency import get_message_service
from src.application.service.service_Interface.group_service import GroupService
from src.application.service.service_Interface.message_service import MessageService
from src.infrastructure.websocket.request_handler import RequestHandler


def get_request_handler(
    message_service: Annotated[MessageService, Depends(get_message_service)],
    group_service: Annotated[GroupService, Depends(get_group_service)],
) -> RequestHandler:
    return RequestHandler(message_service=message_service, group_service=group_service)
