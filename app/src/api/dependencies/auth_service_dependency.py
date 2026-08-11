
from fastapi import Depends

from app.src.domain.repositories_Interface.user_repository import UserRepository

from src.infrastructure.repositories_implementation.user_repository_impl import UserRepositoryImpl
from src.application.service.services_implementation.auth_service_impl import AuthServiceImpl



user_repository=UserRepositoryImpl()

def get_user_repository():
    return user_repository


def get_auth_service(
        user_repository: UserRepository=Depends(get_user_repository),
        ):
    return AuthServiceImpl(
        user_repository=user_repository
    )

