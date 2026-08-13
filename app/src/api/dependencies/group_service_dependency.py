from fastapi import Depends
from src.application.service.service_Interface.group_service import GroupService
from src.application.service.services_implementation.group_service_impl import (
    GroupServiceImpl,
)
from src.domain.repositories_Interface.group_message_repository import (
    GroupMessageRepository,
)
from src.domain.repositories_Interface.group_repository import GroupRepository
from src.domain.repositories_Interface.user_repository import UserRepository
from src.api.dependencies.repository_dependency import(
    get_user_repository,
    get_group_message_repository,
    get_group_repository
)


def get_group_service(
    group_repository: GroupRepository = Depends(get_group_repository),
    group_message_repository: GroupMessageRepository = Depends(
        get_group_message_repository
    ),
    user_repository: UserRepository = Depends(get_user_repository),
)->GroupService:
    return GroupServiceImpl(
        user_repository=user_repository,
        group_repository=group_repository,
        group_message_repository=group_message_repository,
    )
