from abc import ABC, abstractmethod
from uuid import UUID


class GroupMemberRepository(ABC):
    @abstractmethod
    async def add_member(self, group_id: UUID, user_id: UUID, role: str = "member") -> None:
        pass

    @abstractmethod
    async def is_user_in_group(self, user_id: UUID, group_id: UUID) -> bool:
        pass
