from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from src.domain.entities.MessageStatus import MessageStatus


class Message(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID = Field(default_factory=uuid4)
    sender_id: UUID
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: MessageStatus = Field(default=MessageStatus.SENT)
