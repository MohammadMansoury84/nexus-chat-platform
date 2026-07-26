
from pydantic import BaseModel, ConfigDict,Field,UUID4
from datetime import datetime ,timezone
from uuid import uuid4
from src.models.MessageStatus import MessageStatus

class Message(BaseModel):

    model_config = ConfigDict(validation_assignment=True,populate_by_name=True)
    id: UUID4=Field(default_factory=uuid4, alias="_id")
    sender_id:UUID4 
    receiver_id:UUID4|None
    group_id:UUID4|None
    content: str=Field(min_length=1)
    timestamp: str=Field(default_factory=lambda: datetime.now(timezone.utc))
    status: MessageStatus=Field(default=MessageStatus.SENT)