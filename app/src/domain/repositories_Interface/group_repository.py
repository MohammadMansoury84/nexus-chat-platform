from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.Group import Group
from src.infrastructure.Brief.group.get_group_by_id_brief import GetGroupByIdBrief


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
