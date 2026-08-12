from uuid import UUID

from src.domain.entities.User import User
from src.domain.repositories_Interface.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, user: User) -> User:
        self._users.append(user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        for user in self._users:
            if user.id == user_id:
                return user

        return None

    def get_by_username(self, username: str) -> User | None:
        for user in self._users:
            if user.username == username:
                return user

        return None

    def list_all(self) -> list[User]:
        return self._users
