from abc import ABC, abstractmethod
from uuid import UUID

from src.application.DTO.private_message_dto.chat_message_dto import ChatMessageDTO
from src.application.DTO.private_message_dto.message_dto import MessageDTO


class MessageService(ABC):
    @abstractmethod
    async def send_message(
        self, sender_id: UUID, receiver_id: UUID, content: str
    ) -> MessageDTO:
        pass

    @abstractmethod
    async def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[ChatMessageDTO]:
        pass

    @abstractmethod
    async def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID) -> bool:
        pass

    @abstractmethod
    async def mark_chat_as_read(self, reader_id: UUID, chat_partner_id: UUID) -> list[UUID]:
        pass
