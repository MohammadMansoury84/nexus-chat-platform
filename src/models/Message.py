
from pydantic import BaseModel,Field,UUID4
from datetime import datetime
from uuid import uuid4
from src.models.MessageStatus import MessageStatus

class Message(BaseModel):
    id: UUID4=Field(default_factory=uuid4, alias="_id")
    sender_id:UUID4 | None=None
    content: str | None=None
    timestamp: str=Field(default_factory=lambda: datetime.now().isoformat())
    status: MessageStatus=Field(default=MessageStatus.SENT)