from uuid import UUID

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.domain.entities.MessageStatus import MessageStatus
from src.domain.entities.PrivateChat import PrivateChat
from src.domain.repositories_Interface.private_chat_repositiry import PrivateChatRepository
from src.infrastructure.Brief.private_chat.private_chat_message_brief import (
    PrivateChatMessageBrief,
)
from src.infrastructure.database.orm_models.private_chat_model import PrivateChatModel
from src.infrastructure.database.orm_models.private_message_model import PrivateMessageModel


class PrivateChatRepositoryImpl(PrivateChatRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add(self, private_chat: PrivateChat) -> PrivateChat:
        private_chat_orm = PrivateChatModel(
            id=private_chat.id,
            user1_id=private_chat.user1_id,
            user2_id=private_chat.user2_id,
            created_at=private_chat.created_at,
        )

        self._db.add(private_chat_orm)

        return private_chat

    async def get_private_chat_by_user_ids(
        self, user1_id: UUID, user2_id: UUID
    ) -> UUID | None:

        stmt = select(PrivateChatModel.id).where(
            or_(
                and_(
                    PrivateChatModel.user1_id == user1_id,
                    PrivateChatModel.user2_id == user2_id,
                ),
                and_(
                    PrivateChatModel.user1_id == user2_id,
                    PrivateChatModel.user2_id == user1_id,
                ),
            )
        )

        return (await self._db.scalars(stmt)).first()

    async def get_private_chat_with_messages(
        self,
        user1_id: UUID,
        user2_id: UUID,
    ) -> list[PrivateChatMessageBrief] | None:
        stmt = (
            select(PrivateChatModel)
            .where(
                or_(
                    and_(
                        PrivateChatModel.user1_id == user1_id,
                        PrivateChatModel.user2_id == user2_id,
                    ),
                    and_(
                        PrivateChatModel.user1_id == user2_id,
                        PrivateChatModel.user2_id == user1_id,
                    ),
                )
            )
            .options(
                selectinload(PrivateChatModel.messages).joinedload(
                    PrivateMessageModel.sender
                )
            )
        )

        result = await self._db.scalars(stmt)
        chat_model = result.unique().first()

        if chat_model is None or not chat_model.messages:
            return []

        return [
            PrivateChatMessageBrief(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                sender_username=msg.sender.username,
                content=msg.content,
                status=msg.status,
                timestamp=msg.created_at,
            )
            for msg in chat_model.messages
        ]

    async def mark_messages_as_read(self, message_ids: list[UUID]) -> None:
        stmt = (
            update(PrivateMessageModel)
            .where(PrivateMessageModel.id.in_(message_ids))
            .values(status=MessageStatus.READ)
        )
        await self._db.execute(stmt)
