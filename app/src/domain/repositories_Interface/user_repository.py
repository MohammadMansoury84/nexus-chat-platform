from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr
from src.domain.entities.User import User
from src.infrastructure.Brief.user.get_by_id_brief import GetByIdBrief
from src.infrastructure.Brief.user.get_by_username_brief import GetByUserNameBrief
from src.infrastructure.Brief.user.list_all_brief import ListAllBrief


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> GetByIdBrief | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> GetByUserNameBrief | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[ListAllBrief]:
        pass

    @abstractmethod
    async def is_email_used(self, email: EmailStr) -> bool:
        pass

    @abstractmethod
    async def is_username_used(self, username: str) -> bool:
        pass

    @abstractmethod
    async def get_by_ids(self, user_ids: list[UUID]) -> list[GetByIdBrief]:
        pass
