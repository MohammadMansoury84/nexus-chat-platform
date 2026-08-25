from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatMessageDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    sender_id: UUID
    username: str
    content: str
    status: str
    timestamp: datetime
