from datetime import datetime,timezone
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field,ConfigDict
from src.entities.GroupMessage import GroupMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.User import User

class Group(BaseModel):
    model_config = ConfigDict(validate_assignment=True,populate_by_name=True,strict=True)
    id: UUID4=Field(default_factory=uuid4,strict=True)
    name: str =Field(min_length=4,max_length=150)
    creator_id:UUID4
    created_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    members: list["User"] = Field(default_factory=list)
    messages: list[GroupMessage] = Field(default_factory=list)


from src.entities.User import User

Group.model_rebuild()