from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from typing import Annotated
from fastapi import Depends
from uuid import UUID

from src.domain.repositories_Interface.user_repository import UserRepository
from src.application.security.token_service_interface.token_service import TokenService
from src.api.dependencies.repository_dependency import get_user_repository
from src.api.dependencies.token_service_dependency import get_token_service
from src.core.exceptions.InvalidAccessTokenError import InvalidAccessTokenError




security=HTTPBearer()
user_repository = get_user_repository()

def get_current_user(
        credentials:Annotated[
            HTTPAuthorizationCredentials,
            Depends(security)
        ],
        token_service:Annotated[
            TokenService,
            Depends(get_token_service)
        ],
        user_repository:Annotated[
            UserRepository,
            Depends(get_user_repository)
        ]
    )->UUID :

    user_id=token_service.decode_token(credentials.credentials)


    if user_id is None:
        raise InvalidAccessTokenError(
            "User associated with token was not found."
        )

    return user_id








