from uuid import UUID

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
        request_id: UUID | None,
        data: dict,
    ) -> None:
        pass

    async def handle_send_group_message(
        self,
        user_id: UUID,
        request_id: UUID | None,
        data: dict,
    ) -> None:
        pass
