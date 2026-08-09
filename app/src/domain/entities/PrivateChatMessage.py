from uuid import UUID

from src.domain.entities.Message import Message


class PrivateChatMessage(Message):
    receiver_id: UUID
