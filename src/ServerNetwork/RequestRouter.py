import asyncio
from collections.abc import Awaitable, Callable

from src.entities.RequestType import RequestType

Handler = Callable[[dict, asyncio.StreamWriter], Awaitable[dict]]


class RequestRouter:
    def __init__(self) -> None:
        self._routes: dict[RequestType, Handler] = {}

    def register_route(self, request_type: RequestType, handler: Handler) -> None:
        self._routes[request_type] = handler

    async def dispatch(self, request: dict, writer: asyncio.StreamWriter) -> dict:
        request_type = RequestType(request["request_type"])
        handler = self._routes[request_type]
        return await handler(request.get("data", {}), writer)
