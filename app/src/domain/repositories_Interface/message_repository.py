from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import PrivateChatMessage


class MassageRepository(ABC):
    @abstractmethod
    async def add(self, message: PrivateChatMessage):
        pass

    @abstractmethod
    async def delete_messages_by_chat_id(self, chat_id: UUID) -> None:
        pass
