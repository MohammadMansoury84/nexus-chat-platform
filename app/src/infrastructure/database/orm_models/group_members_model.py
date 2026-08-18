from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.infrastructure.database.orm_models.group_model import GroupModel
    from src.infrastructure.database.orm_models.user_model import UserModel
from src.infrastructure.database.orm_models.base import Base


class GroupMembersModel(Base):
    __tablename__ = "group_members"

    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    role: Mapped[str] = mapped_column(default="member")

    group: Mapped["GroupModel"] = relationship(back_populates="members")
    user: Mapped["UserModel"] = relationship(back_populates="joined_groups")


from src.infrastructure.database.orm_models.group_model import GroupModel
from src.infrastructure.database.orm_models.user_model import UserModel
