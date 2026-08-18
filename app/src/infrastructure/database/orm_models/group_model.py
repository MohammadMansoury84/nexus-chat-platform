from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.group_members_model import GroupMembersModel
    from src.infrastructure.database.orm_models.group_message_model import GroupMessageModel
    from src.infrastructure.database.orm_models.user_model import UserModel
from src.infrastructure.database.orm_models.base import Base


class GroupModel(Base):
    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    creator: Mapped["UserModel"] = relationship(back_populates="groups_created")

    members: Mapped[list["GroupMembersModel"]] = relationship(
        back_populates="group", cascade="all , delete-orphan"
    )

    messages: Mapped[list["GroupMessageModel"]] = relationship(
        back_populates="group",
        cascade="all , delete-orphan",
        order_by="GroupMessageModel.created_at",
    )


from src.infrastructure.database.orm_models.group_members_model import (
    GroupMembersModel,
)
from src.infrastructure.database.orm_models.group_message_model import (
    GroupMessageModel,
)
from src.infrastructure.database.orm_models.user_model import UserModel
