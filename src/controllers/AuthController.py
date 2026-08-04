from uuid import UUID

from src.entities.User import User
from src.service.AuthService import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    def signup(self, username: str, email: str, password: str) -> UUID | None:
        return self._auth_service.signup(username=username, email=email, password=password)

    def login(self, username: str, password: str) -> User | None:
        return self._auth_service.login(username=username, password=password)

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self._auth_service.get_user_by_id(user_id=user_id)

    def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID,
        logged_in_user_ids: set[UUID],
    ) -> list[dict]:

        return self._auth_service.get_other_logged_in_users_for_show(
            current_user_id=current_user_id,
            logged_in_user_ids=logged_in_user_ids,
        )

    def get_all_users(self) -> list[User]:
        return self._auth_service.get_all_users()
