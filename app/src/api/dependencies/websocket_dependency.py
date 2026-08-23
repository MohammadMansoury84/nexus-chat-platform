from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, WebSocket, status
from src.api.dependencies.repository_dependency import get_user_repository
from src.api.dependencies.token_service_dependency import get_token_service
from src.application.security.token_service_interface.token_service import (
    TokenService,
)
from src.domain.repositories_Interface.user_repository import UserRepository
from src.infrastructure.websocket.connection_manager import ConnectionManager

_connection_manager = ConnectionManager()


@lru_cache
def get_connection_manager() -> ConnectionManager:
    return _connection_manager


async def get_current_websocket_user_id(
    websocket: WebSocket,
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UUID:

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication token is required.",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token missing")

    try:
        user_id = token_service.decode_token(token)
    except Exception:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid authentication token.",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await user_repository.get_by_id(user_id)

    if user is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User associated with token was not found.",
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_id
