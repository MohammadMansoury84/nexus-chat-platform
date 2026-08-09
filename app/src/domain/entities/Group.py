from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict, Field

from src.domain.entities.GroupMessage import GroupMessage

if TYPE_CHECKING:
    from src.domain.entities.User import User


class Group(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID4 = Field(default_factory=uuid4, strict=True)
    name: str = Field(min_length=4, max_length=150)
    creator_id: UUID4
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    members: list["User"] = Field(default_factory=list)
    messages: list[GroupMessage] = Field(default_factory=list)


from src.domain.entities.User import User  # noqa: E402

Group.model_rebuild()
