from fastapi import Depends
from src.api.dependencies.repository_dependency import (
    get_message_repository,
    get_private_chat_repository,
    get_redis_online_user_repository,
    get_user_repository,
)
from src.application.service.service_Interface.message_service import MessageService
from src.application.service.services_implementation.message_service_impl import (
    MessageServiceImpl,
)
from src.domain.repositories_Interface.message_repository import MassageRepository
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository


def get_message_service(
    user_repository: UserRepository = Depends(get_user_repository),
    private_chat_repository: PrivateChatRepository = Depends(get_private_chat_repository),
    online_user_repository: RedisOnlineUserRepository = Depends(
        get_redis_online_user_repository
    ),
    message_repository: MassageRepository = Depends(get_message_repository),
) -> MessageService:
    return MessageServiceImpl(
        user_repository=user_repository,
        privateChat_repository=private_chat_repository,
        online_user_repository=online_user_repository,
        message_repository=message_repository,
    )
