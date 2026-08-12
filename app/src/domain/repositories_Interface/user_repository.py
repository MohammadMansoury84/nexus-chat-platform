from uuid import UUID
from abc import ABC, abstractmethod
from src.domain.entities.User import User


class UserRepository(ABC):
    
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass


    @abstractmethod
    def get_by_username(
        self,
        username: str
    ) -> User | None:
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        pass