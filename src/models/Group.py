from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field

from src.models.Message import Message
from src.models.User import User

class Group(BaseModel):
    id: UUID4=Field(default_factory=UUID4, alias="_id")
    name: str | None=None
    creator_id:UUID4 | None=None
    created_at: str=Field(default_factory=lambda: datetime.now().isoformat())
    members: list[User] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)
    