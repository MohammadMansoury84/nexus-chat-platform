from uuid import UUID

from src.entities.Message import Message
from src.service.MessageService import MessageService


class MessageController:
    def __init__(self, message_service: MessageService) -> None:
        self._message_service = message_service

    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        return self._message_service.send_message(
            sender_id=sender_id, receiver_id=receiver_id, content=content
        )

    def get_chat(self, user1_id: UUID, user2_id: UUID) -> list[dict]:
        return self._message_service.get_chat(user1_id=user1_id, user2_id=user2_id)

    def delete_private_chat_history(self, user1_id: UUID, user2_id: UUID):

        return self._message_service.delete_private_chat_history(
            user1_id=user1_id, user2_id=user2_id
        )
