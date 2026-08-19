from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies.database_dependency import get_session
from src.domain.repositories_Interface.group_message_repository import (
    GroupMessageRepository,
)
from src.domain.repositories_Interface.group_repository import GroupRepository
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.repositories_implementation.group_message_repository_impl import (
    GroupMessageRepositoryImpl,
)
from src.infrastructure.repositories_implementation.group_repository_impl import (
    GroupRepositoryImpl,
)
from src.infrastructure.repositories_implementation.private_chat_repositiry_impl import (
    PrivateChatRepositoryImpl,
)
from src.infrastructure.repositories_implementation.user_repository_impl import (
    UserRepositoryImpl,
)

_group_repository = GroupRepositoryImpl()
_group_message_repository = GroupMessageRepositoryImpl()
_private_chat_repository = PrivateChatRepositoryImpl()


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepositoryImpl(db=db)


def get_group_repository() -> GroupRepository:
    return _group_repository


def get_group_message_repository() -> GroupMessageRepository:
    return _group_message_repository


def get_private_chat_repository() -> PrivateChatRepository:
    return _private_chat_repository
