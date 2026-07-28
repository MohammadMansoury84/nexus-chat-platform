
from uuid import UUID
from src.entities.User import User
from src.service.AuthService import AuthService

class AuthController:

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service


    def signup(self, username: str, email: str, password: str)->UUID | None:
        return self._auth_service.signup(username=username,email=email,password=password)


    def login(self, username: str, password: str)-> User | None:
        return self._auth_service.login(username=username,password=password)

    def get_user_by_id(self, user_id: UUID)-> User |None :
        return self._auth_service.get_user_by_id(user_id=user_id)


    def get_all_users_for_show_users(self)->list[dict]:
        return self._auth_service.get_all_users_for_show_users()

    def get_all_users(self)->list[User]:
        return self._auth_service.get_all_users()
    