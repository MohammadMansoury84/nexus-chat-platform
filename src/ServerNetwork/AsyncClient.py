import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable

from src.entities.DTO.Request.RequestModel import RequestModel
from src.entities.RequestType import RequestType
from src.Exceptions.ClientConnectionError import ClientConnectionError
from src.Exceptions.EmptyDataException import EmptyDataException
from src.Exceptions.ResponseError import ResponseError

EventCallback = Callable[[dict], Awaitable[None]]


class AsyncClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._listen_task: asyncio.Task[None] | None = None
        self._pending: dict[str, asyncio.Future[None]] = {}
        self._event_callback: EventCallback | None = None

    def set_event_callback(self, callback: EventCallback) -> None:
        self._event_callback = callback

    async def connet(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self._host, self._host)
        self._listen_task = asyncio.create_task(self._listen_server())

    async def send_request(self, request_type: RequestType, data: dict | None = None):
        if not self._writer:
            raise ClientConnectionError("Client is not connected.")
        request = RequestModel(request_type=request_type, data=data)

        loop = asyncio.get_running_loop()

        future: asyncio.Future[dict] = loop.create_future()

        self._pending[request.request_id] = future

        raw = json.dumps(request.model_dump(), default=str) + "\n"
        self._writer.write(raw.encode("utf-8"))
        await self._writer.drain()

        response = await future
        if not response.get("ok", False):
            raise ResponseError(response.get("message", "Request failed."))
        return response.get("data", {})

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

        if self._listen_task is not None:
            self._listen_task.cancel()
            await asyncio.gather(self._listen_task, return_exceptions=True)
            self._listen_task = None

    async def _listen_server(self) -> None:
        if self._reader is None:
            raise ClientConnectionError("Client is not connected.")

        while True:
            raw = await self._reader.readline()
            if not raw:
                raise EmptyDataException("You cannot send an empty message.")

            message: dict[str, str] = json.loads(raw.decode("utf-8"))
            if message.get("message_type") == "response":
                request_id = message.get("request_id")
                future: asyncio.Future[dict] = self._pending.pop(request_id, None)
                if future is not None and not future.done():
                    future.set_result(message)
                continue
            if message.get("message_type") == "event":
                result = self._event_callback(message)
                if inspect.isawaitable(result):
                    await result
