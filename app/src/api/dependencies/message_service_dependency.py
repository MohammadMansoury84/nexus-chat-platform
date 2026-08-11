
from fastapi import Depends
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure. repositories_implementation.private_chat_repositiry_impl import PrivateChatRepositoryImpl
from src.infrastructure.repositories_implementation.user_repository_impl import UserRepositoryImpl
from src.application.service.services_implementation.message_service_impl import MessageServiceImpl






user_repository=UserRepositoryImpl()
private_chat_repository=PrivateChatRepositoryImpl()

def get_user_repository():
    return user_repository

def get_private_chat_repository():
    return private_chat_repository


def get_message_service(
        user_repository: UserRepository=Depends(get_user_repository),
        private_chat_repository:PrivateChatRepository=Depends(get_private_chat_repository),
        ):
    return MessageServiceImpl(
        user_repository=user_repository,
        privateChat_repository=private_chat_repository,
        )

