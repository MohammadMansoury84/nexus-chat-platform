from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr
from src.domain.entities.User import User
from src.infrastructure.Brief.get_by_id_brief import GetByIdBrief
from src.infrastructure.Brief.get_by_username_brief import GetByUserNameBrief


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> GetByIdBrief | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> GetByUserNameBrief | None:
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        pass

    @abstractmethod
    def is_email_used(self, email: EmailStr) -> bool:
        pass

    @abstractmethod
    def is_username_used(self, username: str) -> bool:
        pass

    @abstractmethod
    def add_user_id_to_logged_in_user_ids(self, user_id: UUID) -> UUID:
        pass

    @abstractmethod
    def remove_user_id_in_logged_in_user_ids(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    def get_logged_in_user_ids(self) -> set[UUID]:
        pass

    @abstractmethod
    def is_user_logged_in(self, user_id: UUID) -> bool:
        pass
