from fastapi import Depends
from src.application.service.services_implementation.message_service_impl import (
    MessageServiceImpl,
)
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.user_repository import UserRepository
from src.api.dependencies.repository_dependency import(
    get_user_repository,
    get_private_chat_repository
)



def get_message_service(
    user_repository: UserRepository = Depends(get_user_repository),
    private_chat_repository: PrivateChatRepository = Depends(get_private_chat_repository),
):
    return MessageServiceImpl(
        user_repository=user_repository,
        privateChat_repository=private_chat_repository,
    )
