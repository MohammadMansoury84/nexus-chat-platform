from uuid import UUID

from src.domain.entities.User import User
from src.domain.repositories_Interface.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self) -> None:
        self._users: list[User] = []
        self._logged_in_user_ids: set[UUID] = set()

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

    def add_user_id_to_logged_in_user_ids(self, user_id: UUID) -> UUID:
        self._logged_in_user_ids.add(user_id)
        return user_id

    def remove_user_id_in_logged_in_user_ids(self, user_id: UUID) -> None:

        if user_id in self._logged_in_user_ids:
            self._logged_in_user_ids.remove(user_id)

    def get_logged_in_user_ids(self) -> set[UUID]:
        return self._logged_in_user_ids

    def is_user_logged_in(self, user_id: UUID) -> bool:
        return user_id in self._logged_in_user_ids
