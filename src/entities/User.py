from datetime import datetime, timezone
from uuid import uuid4,UUID
from src.entities.PrivateChat import PrivateChat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities.Group import Group

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True,populate_by_name=True,strict=True)
    id: UUID=Field(default_factory=uuid4)
    username: str=Field(min_length=4,max_length=20)
    email: EmailStr
    password: str=Field(min_length=6,max_length=150)
    created_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    private_chats: list[PrivateChat]= Field(default_factory=list)
    groups_created: list["Group"] = Field(default_factory=list)
    joined_groups: list["Group"] = Field(default_factory=list)



from src.entities.Group import Group

User.model_rebuild()