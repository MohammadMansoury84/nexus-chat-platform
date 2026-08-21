from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.private_chat_model import PrivateChatModel
    from src.infrastructure.database.orm_models.user_model import UserModel
from src.infrastructure.database.orm_models.base import Base


class PrivateMessageModel(Base):
    __tablename__ = "private_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    chat_id: Mapped[UUID] = mapped_column(
        ForeignKey("private_chats.id", ondelete="CASCADE"), index=True
    )

    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="SENT")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    chat: Mapped["PrivateChatModel"] = relationship(back_populates="messages")

    sender: Mapped["UserModel"] = relationship()


from src.infrastructure.database.orm_models.private_chat_model import (
    PrivateChatModel,
)
from src.infrastructure.database.orm_models.user_model import UserModel
