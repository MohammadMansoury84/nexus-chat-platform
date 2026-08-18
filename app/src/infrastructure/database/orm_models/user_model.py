from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.group_members_model import GroupMembersModel
    from src.infrastructure.database.orm_models.group_model import GroupModel
    from src.infrastructure.database.orm_models.private_chat_model import PrivateChatModel

from src.infrastructure.database.orm_models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    groups_created: Mapped[list["GroupModel"]] = relationship(
        back_populates="creator",
        cascade="all,delete-orphan",
    )

    joined_groups: Mapped[list["GroupMembersModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    private_chats_as_user1: Mapped[list["PrivateChatModel"]] = relationship(
        foreign_keys="PrivateChatModel.user1_id",
        back_populates="user1",
    )

    private_chats_as_user2: Mapped[list["PrivateChatModel"]] = relationship(
        foreign_keys="PrivateChatModel.user2_id",
        back_populates="user2",
    )


from src.infrastructure.database.orm_models.group_members_model import (
    GroupMembersModel,
)
from src.infrastructure.database.orm_models.group_model import GroupModel
from src.infrastructure.database.orm_models.private_chat_model import (
    PrivateChatModel,
)
