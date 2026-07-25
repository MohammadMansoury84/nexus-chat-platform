import pydantic,datetime,MessageStatus
from pydantic import BaseModel,Field,UUID4

class Message(BaseModel):
    id: UUID4=Field(default_factory=UUID4, alias="_id")
    sender_id:UUID4 | None=None
    content: str | None=None
    timestamp: str=Field(default_factory=lambda: datetime.now().isoformat())
    status: MessageStatus=Field(default=MessageStatus.SENT)