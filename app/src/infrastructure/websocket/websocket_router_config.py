from src.api.schemas.WebSocket.websocket_action import WebSocketAction
from src.infrastructure.websocket.request_handler import RequestHandler
from src.infrastructure.websocket.request_router import RequestRouter


def create_websocket_router(request_handler: RequestHandler) -> RequestRouter:
    router = RequestRouter()

    router.register_route(
        WebSocketAction.SEND_PRIVATE_MESSAGE,
        request_handler.handle_send_private_message,
    )
    router.register_route(
        WebSocketAction.SEND_GROUP_MESSAGE,
        request_handler.handle_send_group_message,
    )
    router.register_route(
        WebSocketAction.MESSAGE_READ,
        request_handler.handel_message_read,
    )

    return router
