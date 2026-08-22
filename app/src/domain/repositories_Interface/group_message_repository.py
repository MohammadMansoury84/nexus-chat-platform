from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.GroupMessage import GroupMessage


class GroupMessageRepository(ABC):
    @abstractmethod
    async def add(self, group_message: GroupMessage) -> GroupMessage:
        pass

    @abstractmethod
    async def delete_group_chat(self, group_id: UUID) -> None:
        pass
