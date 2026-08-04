import asyncio
import json
from typing import Any
from uuid import UUID

from src.entities.DTO.Response.ResponseModel import ResponseModel


class ConnectionManagement:
    def __init__(self) -> None:
        self._writers_by_user: dict[UUID, asyncio.StreamWriter] = {}
        self._users_by_writer: dict[asyncio.StreamWriter, UUID] = {}
        self.locks: dict[asyncio.StreamWriter, asyncio.Lock] = {}

    def add_connection(self, writer: asyncio.StreamWriter) -> None:
        self.locks[writer] = asyncio.Lock()

    def login(self, user_id: UUID, writer: asyncio.StreamWriter) -> None:

        if self._is_connection_authenticated(writer):
            old_user_id = self._users_by_writer.get(writer)
            self._writers_by_user.pop(old_user_id, None)

        self._writers_by_user[user_id] = writer
        self._users_by_writer[writer] = user_id

    def _is_connection_authenticated(self, writer: asyncio.StreamWriter) -> bool:
        return writer in self._users_by_writer

    def get_logged_in_users(self, writer: asyncio.StreamWriter) -> UUID | None:
        if not self._is_connection_authenticated(writer):
            return None
        return self._users_by_writer.get(writer)

    def logout(self, writer: asyncio.StreamWriter) -> None:
        user_id = self._users_by_writer.pop(writer, None)
        if user_id:
            self._writers_by_user.pop(user_id, None)

    def remove_connection(self, writer: asyncio.StreamWriter) -> None:
        self.logout(writer)
        self.locks.pop(writer, None)

    async def send(
        self,
        writer: asyncio.StreamWriter,
        message: ResponseModel | dict[str, Any],
    ) -> None:
        lock = self.locks.get(writer)

        if lock is None:
            lock = asyncio.Lock()
            self.locks[writer] = lock

        if hasattr(message, "model_dump"):
            payload = message.model_dump(mode="json")
        else:
            payload = message

        async with lock:
            data = json.dumps(payload, default=str) + "\n"

            writer.write(data.encode("utf-8"))
            await writer.drain()

    async def send_to_user(self, user_id: UUID, message: dict) -> bool:
        writer = self._writers_by_user.get(user_id)
        if writer:
            await self.send(writer, message)
            return True

        return False

    def get_logged_in_user_ids(self) -> set[UUID]:
        return set(self._writers_by_user.keys())
