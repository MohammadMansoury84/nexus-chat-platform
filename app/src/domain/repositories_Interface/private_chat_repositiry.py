from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.PrivateChat import PrivateChat
from src.infrastructure.Brief.private_chat.private_chat_message_brief import (
    PrivateChatMessageBrief,
)


class PrivateChatRepository(ABC):
    @abstractmethod
    async def add(self, private_chat: PrivateChat) -> PrivateChat:
        pass

    @abstractmethod
    async def get_private_chat_by_user_ids(
        self, user1_id: UUID, user2_id: UUID
    ) -> UUID | None:
        pass

    @abstractmethod
    async def get_private_chat_with_messages(
        self, user1_id: UUID, user2_id: UUID
    ) -> list[PrivateChatMessageBrief] | None:

        pass

    @abstractmethod
    async def mark_messages_as_read(self, message_ids: list[UUID]) -> None:
        pass
