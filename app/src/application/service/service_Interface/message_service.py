from abc import ABC, abstractmethod
from uuid import UUID
from src.domain.entities.Message import Message

class MessageService(ABC):

    @abstractmethod
    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        pass

    @abstractmethod
    def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[dict]:
        pass

    @abstractmethod
    def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID) -> bool:
        pass

