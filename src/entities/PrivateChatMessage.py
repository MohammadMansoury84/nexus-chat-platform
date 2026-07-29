from uuid import UUID

from src.entities.Message import Message


class PrivateChatMessage(Message):
    receiver_id: UUID
