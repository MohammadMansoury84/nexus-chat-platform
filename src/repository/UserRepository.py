from uuid import UUID

from src.entities.User import User


class UserRepository:
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

    def list_all(self) -> list[User]:
        return self._users
