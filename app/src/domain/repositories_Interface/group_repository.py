from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.Group import Group
from src.infrastructure.Brief.group.get_all_groups_for_show_users_brief import (
    GetAllGroupsForShowUsersBrief,
)
from src.infrastructure.Brief.group.get_group_by_id_brief import GetGroupByIdBrief
from src.infrastructure.Brief.group.group_chat_message_brief import GroupChatMessageBrief


class GroupRepository(ABC):
    @abstractmethod
    async def add(self, group: Group) -> Group:
        pass

    @abstractmethod
    async def get_by_id(self, group_id: UUID) -> GetGroupByIdBrief | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Group]:
        pass

    @abstractmethod
    async def remove_group(self, group: Group) -> bool:
        pass

    @abstractmethod
    async def get_group_with_messages(self, group_id: UUID) -> list[GroupChatMessageBrief]:
        pass

    @abstractmethod
    async def get_all_groups_for_show_users(
        self, user_id: UUID
    ) -> list[GetAllGroupsForShowUsersBrief]:

        pass
