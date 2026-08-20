from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from src.api.dependencies.repository_dependency import (
    get_redis_online_user_repository,
    get_user_repository,
)
from src.api.dependencies.token_service_dependency import (
    get_passweord_hasher,
    get_token_service,
)
from src.application.security.password_hasher import PasswordHasher
from src.application.security.token_service_interface.token_service import TokenService
from src.application.service.service_Interface.auth_service import AuthService
from src.application.service.services_implementation.auth_service_impl import (
    AuthServiceImpl,
)
from src.core.exceptions import InvalidAccessTokenError
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository

_security = HTTPBearer()


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    passweord_hasher: PasswordHasher = Depends(get_passweord_hasher),
    token_service: TokenService = Depends(get_token_service),
    online_user_repository: RedisOnlineUserRepository = Depends(
        get_redis_online_user_repository
    ),
) -> AuthService:
    return AuthServiceImpl(
        user_repository=user_repository,
        passweord_hasher=passweord_hasher,
        token_service=token_service,
        online_user_repository=online_user_repository,
    )


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_security)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UUID:

    user_id = token_service.decode_token(credentials.credentials)

    user = user_repository.get_by_id(user_id)

    if user is None:
        raise InvalidAccessTokenError("User associated with token was not found.")

    if user_id is None:
        raise InvalidAccessTokenError("User associated with token was not found.")

    return user_id
