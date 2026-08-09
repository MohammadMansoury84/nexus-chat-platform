from uuid import UUID

from src.domain.entities.Message import Message


class GroupMessage(Message):
    group_id: UUID
