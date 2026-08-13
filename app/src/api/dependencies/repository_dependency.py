
from src.infrastructure.repositories_implementation.group_message_repository_impl import (
    GroupMessageRepositoryImpl,
)
from src.infrastructure.repositories_implementation.group_repository_impl import (
    GroupRepositoryImpl,
)
from src.infrastructure.repositories_implementation.user_repository_impl import (
    UserRepositoryImpl,
)
from src.infrastructure.repositories_implementation.private_chat_repositiry_impl import (
    PrivateChatRepositoryImpl,
)

user_repository = UserRepositoryImpl()
group_repository = GroupRepositoryImpl()
group_message_repository = GroupMessageRepositoryImpl()
private_chat_repository = PrivateChatRepositoryImpl()


def get_user_repository():
    return user_repository


def get_group_repository():
    return group_repository


def get_group_message_repository():
    return group_message_repository


def get_private_chat_repository():
    return private_chat_repository
