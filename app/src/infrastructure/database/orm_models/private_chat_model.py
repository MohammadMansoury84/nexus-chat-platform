from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.private_message_model import (
        PrivateMessageModel,
    )
    from src.infrastructure.database.orm_models.user_model import UserModel
from src.infrastructure.database.orm_models.base import Base


class PrivateChatModel(Base):
    __tablename__ = "private_chats"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    user1_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user2_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    messages: Mapped[list["PrivateMessageModel"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )

    user1: Mapped["UserModel"] = relationship(
        foreign_keys=[user1_id],
        back_populates="private_chats_as_user1",
    )

    user2: Mapped["UserModel"] = relationship(
        foreign_keys=[user2_id],
        back_populates="private_chats_as_user2",
    )

    __table_args__ = (
        UniqueConstraint(
            "user1_id",
            "user2_id",
            name="uq_private_chat_users",
        ),
    )


from src.infrastructure.database.orm_models.private_message_model import (
    PrivateMessageModel,
)
from src.infrastructure.database.orm_models.user_model import UserModel
