import asyncio
import json
from asyncio import Server

from pydantic import ValidationError

from src.core.CustomeLogger import CustomLogger
from src.entities.DTO.Response.ResponseModel import ResponseModel
from src.Exceptions.EmptyDataException import EmptyDataException
from src.ServerNetwork.ConnectionManagement import ConnectionManagement
from src.ServerNetwork.RequestRouter import RequestRouter


class AsyncServer:
    def __init__(
        self,
        host: str,
        port: int,
        requestrouter: RequestRouter,
        connectionmanagement: ConnectionManagement,
    ):

        self._host = host
        self._port = port
        self._requestRouter = requestrouter
        self._connectionManagement = connectionmanagement
        self._server: Server | None = None
        self.custome_logger = CustomLogger(self.__class__.__name__)

    async def start(self) -> None:

        self._server = await asyncio.start_server(
            self._handle_client, self._host, self._port
        )

        self.custome_logger.info("Starting server", host=self._host, port=self._port)

    async def serve_forever(self) -> None:

        if self._server is None:
            await self.start()

        async with self._server:
            await self._server.serve_forever()

    async def close(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self.custome_logger.info("Server closed")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:

        self._connectionManagement.add_connection(writer)
        self.custome_logger.info(
            "New client connected", client_address=writer.get_extra_info("peername")
        )

        try:
            while True:
                data = await reader.readline()

                if not data:
                    raise EmptyDataException("Data cannot be empty")

                request = json.loads(data.decode("utf-8"))

                try:
                    response = await self._requestRouter.dispatch(request, writer)

                    response = ResponseModel(
                        request_id=request.get("request_id"), status=True, data=response
                    )

                except Exception as e:
                    self.custome_logger.exception("Error processing request", error=str(e))
                    response = ResponseModel(
                        request_id=request.get("request_id"),
                        status=False,
                        data={"message": self._get_error_message(e)},
                    )

                await self._connectionManagement.send(writer, response)

        finally:
            self._connectionManagement.remove_connection(writer)
            writer.close()
            await writer.wait_closed()
            self.custome_logger.info(
                "Client disconnected", client_address=writer.get_extra_info("peername")
            )

    @staticmethod
    def _get_error_message(error: Exception) -> str:
        if isinstance(error, ValidationError):
            messages: list[str] = []

            for item in error.errors():
                field = ".".join(str(part) for part in item["loc"])
                message = item["msg"]

                messages.append(f"{field}: {message}")

            return " | ".join(messages)

        return str(error) or "An unexpected server error occurred."
