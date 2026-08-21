from uuid import UUID

from src.domain.entities.Message import Message


class PrivateChatMessage(Message):
    chat_id: UUID
    receiver_id: UUID
