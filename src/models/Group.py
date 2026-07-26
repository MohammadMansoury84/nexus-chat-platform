from datetime import datetime,timezone
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field
from src.models.Message import Message
from src.models.User import User

class Group(BaseModel):
    id: UUID4=Field(default_factory=uuid4,strict=True)
    name: str =Field(min_length=4,max_length=150)
    creator_id:UUID4
    created_at: str=Field(default_factory=lambda: datetime.now(timezone.utc))
    members: list[User] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)
    