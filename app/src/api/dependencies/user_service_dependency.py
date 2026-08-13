
from typing import Annotated
from fastapi import Depends
from uuid import UUID

from src.application.service.services_implementation.user_service_impl import UserServiceImpl
from src.application.service.service_Interface.user_service import UserService
from src.domain.repositories_Interface.user_repository import UserRepository
from src.api.dependencies.repository_dependency import get_user_repository


def get_user_service(
    user_repository:UserRepository=Depends(get_user_repository)
    )->UserService:
    return UserServiceImpl(
        user_repository=user_repository
    )





    

















