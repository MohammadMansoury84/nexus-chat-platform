from uuid import UUID
from abc import ABC, abstractmethod
from src.domain.entities.Group import Group

class GroupRepository(ABC):

    @abstractmethod
    def add(self, group: Group) -> Group:
        pass

    @abstractmethod
    def get_by_id(self, group_id: UUID) -> Group | None:
        pass

    @abstractmethod
    def list_all(self) -> list[Group]:
        pass

    @abstractmethod
    def remove_group(self, group: Group) -> bool:
        pass