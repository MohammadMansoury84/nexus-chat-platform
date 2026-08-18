from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.group_model import GroupModel
    from src.infrastructure.database.orm_models.user_model import UserModel
from src.infrastructure.database.orm_models.base import Base


class GroupMessageModel(Base):
    __tablename__ = "group_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    sender_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), index=True
    )

    content: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(default="SENT")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    group: Mapped["GroupModel"] = relationship(back_populates="messages")
    sender: Mapped["UserModel"] = relationship()


from src.infrastructure.database.orm_models.group_model import GroupModel
from src.infrastructure.database.orm_models.user_model import UserModel
