from abc import ABC, abstractmethod
from uuid import UUID
from src.application.DTO.private_message_dto.message_dto import MessageDTO
from src.application.DTO.private_message_dto.chat_message_dto import ChatMessageDTO

class MessageService(ABC):

    @abstractmethod
    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> MessageDTO:
        pass

    @abstractmethod
    def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[ChatMessageDTO]:
        pass

    @abstractmethod
    def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID) -> bool:
        pass

