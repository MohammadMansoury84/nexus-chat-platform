from fastapi import Depends
from src.application.security.password_hasher import PasswordHasher
from src.application.service.services_implementation.auth_service_impl import (
    AuthServiceImpl,
)
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.repositories_implementation.user_repository_impl import (
    UserRepositoryImpl,
)
from src.infrastructure.security.password_hasher_impl import PasswordHasherImpl

user_repository = UserRepositoryImpl()
passweord_hasher = PasswordHasherImpl()


def get_user_repository():
    return user_repository


def get_passweord_hasher():
    return passweord_hasher


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    passweord_hasher: PasswordHasher = Depends(get_passweord_hasher),
):
    return AuthServiceImpl(user_repository=user_repository)
