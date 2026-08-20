from fastapi import Depends
from src.api.dependencies.repository_dependency import (
    get_redis_online_user_repository,
    get_user_repository,
)
from src.application.service.service_Interface.user_service import UserService
from src.application.service.services_implementation.user_service_impl import (
    UserServiceImpl,
)
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    online_user_repository: RedisOnlineUserRepository = Depends(
        get_redis_online_user_repository
    ),
) -> UserService:
    return UserServiceImpl(
        user_repository=user_repository, online_user_repository=online_user_repository
    )
