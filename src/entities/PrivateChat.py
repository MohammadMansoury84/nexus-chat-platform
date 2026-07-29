from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from src.entities.PrivateChatMessage import PrivateChatMessage


class PrivateChat(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID = Field(default_factory=uuid4)
    user1_id: UUID
    user2_id: UUID
    messages: list[PrivateChatMessage] = Field(default_factory=list)
