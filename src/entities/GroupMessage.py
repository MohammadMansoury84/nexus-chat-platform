from uuid import UUID

from src.entities.Message import Message


class GroupMessage(Message):
    group_id: UUID
