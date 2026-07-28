from uuid import uuid4,UUID
from pydantic import BaseModel, Field, ConfigDict
from src.entities.Message import Message

class PrivateChat(BaseModel):
    model_config = ConfigDict(validate_assignment=True,populate_by_name=True,strict=True)
    id: UUID = Field(default_factory=uuid4)
    user1_id: UUID
    user2_id: UUID
    messages: list[Message] = Field(default_factory=list)

