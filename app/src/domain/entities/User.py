from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.domain.entities.PrivateChat import PrivateChat

if TYPE_CHECKING:
    from src.domain.entities.Group import Group

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID = Field(default_factory=uuid4)
    username: str = Field(min_length=4, max_length=20)
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    private_chats: list[PrivateChat] = Field(default_factory=list)
    groups_created: list["Group"] = Field(default_factory=list)
    joined_groups: list["Group"] = Field(default_factory=list)


from src.domain.entities.Group import Group  # noqa: E402

User.model_rebuild()
