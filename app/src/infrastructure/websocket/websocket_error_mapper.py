from src.api.schemas.WebSocket.websocket_error_code import WebSocketErrorCode
from src.core.exceptions.AuthorizationError import AuthorizationError
from src.core.exceptions.ExpiredAccessTokenError import ExpiredAccessTokenError
from src.core.exceptions.GroupNotFoundError import GroupNotFoundError
from src.core.exceptions.InvalidAccessTokenError import InvalidAccessTokenError
from src.core.exceptions.PrivateChatNotFoundError import PrivateChatNotFoundError
from src.core.exceptions.UserAlreadyInGroupError import UserAlreadyInGroupError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.exceptions.UserNotInGroupError import UserNotInGroupError


def map_exception_to_websocket_error(exc: Exception) -> str:

    if isinstance(exc, AuthorizationError):
        return WebSocketErrorCode.UNAUTHORIZED

    if isinstance(exc, InvalidAccessTokenError):
        return WebSocketErrorCode.INVALID_TOKEN

    if isinstance(exc, ExpiredAccessTokenError):
        return WebSocketErrorCode.EXPIRED_TOKEN

    if isinstance(exc, UserNotFoundError):
        return WebSocketErrorCode.USER_NOT_FOUND

    if isinstance(exc, GroupNotFoundError):
        return WebSocketErrorCode.GROUP_NOT_FOUND

    if isinstance(exc, PrivateChatNotFoundError):
        return WebSocketErrorCode.PRIVATE_CHAT_NOT_FOUND

    if isinstance(exc, UserAlreadyInGroupError):
        return WebSocketErrorCode.USER_ALREADY_IN_GROUP

    if isinstance(exc, UserNotInGroupError):
        return WebSocketErrorCode.USER_NOT_IN_GROUP

    return WebSocketErrorCode.INTERNAL_SERVER_ERROR
