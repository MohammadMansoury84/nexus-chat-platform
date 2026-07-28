from src.entities.Message import Message
from uuid import UUID

class PrivateChatMessage(Message):
    receiver_id: UUID