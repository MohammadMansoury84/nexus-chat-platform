from fastapi import Depends
from src.application.security.password_hasher import PasswordHasher
from src.application.service.services_implementation.auth_service_impl import (
    AuthServiceImpl,
)
from src.domain.repositories_Interface.user_repository import UserRepository
from src.application.security.token_service_interface.token_service import TokenService
from src.api.dependencies.repository_dependency import get_user_repository
from src.api.dependencies.token_service_dependency import (
    get_token_service,
    get_passweord_hasher
    )


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    passweord_hasher: PasswordHasher = Depends(get_passweord_hasher),
    token_service: TokenService =Depends(get_token_service)
):
    return AuthServiceImpl(
        user_repository=user_repository,
        passweord_hasher=passweord_hasher,
        token_service=token_service
        )
