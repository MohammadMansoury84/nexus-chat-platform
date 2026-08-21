from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities import PrivateChatMessage
from src.domain.repositories_Interface.message_repository import MassageRepository
from src.infrastructure.database.orm_models.private_message_model import PrivateMessageModel


class MassageRepositoryImpl(MassageRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add(self, message: PrivateChatMessage):
        private_message_model = PrivateMessageModel(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            content=message.content,
            status=message.status,
            created_at=message.timestamp,
        )

        self._db.add(private_message_model)

        return message

    async def delete_messages_by_chat_id(self, chat_id: UUID) -> None:
        stmt = delete(PrivateMessageModel).where(PrivateMessageModel.chat_id == chat_id)
        await self._db.execute(stmt)
