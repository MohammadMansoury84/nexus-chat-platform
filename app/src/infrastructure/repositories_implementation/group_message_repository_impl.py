from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.GroupMessage import GroupMessage
from src.domain.repositories_Interface.group_message_repository import (
    GroupMessageRepository,
)
from src.infrastructure.database.orm_models.group_message_model import GroupMessageModel


class GroupMessageRepositoryImpl(GroupMessageRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add(self, group_message: GroupMessage) -> GroupMessage:

        orm_message = GroupMessageModel(
            id=group_message.id,
            sender_id=group_message.sender_id,
            group_id=group_message.group_id,
            content=group_message.content,
            status=group_message.status,
            created_at=group_message.timestamp,
        )

        self._db.add(orm_message)

        return group_message

    async def delete_group_chat(self, group_id: UUID) -> None:
        stmt = delete(GroupMessageModel).where(GroupMessageModel.group_id == group_id)
        await self._db.execute(statement=stmt)
