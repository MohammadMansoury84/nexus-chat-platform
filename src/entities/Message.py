
from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime ,timezone
from uuid import uuid4,UUID
from src.entities.MessageStatus import MessageStatus

class Message(BaseModel):

    model_config = ConfigDict(validate_assignment=True,populate_by_name=True,strict=True)
    id: UUID=Field(default_factory=uuid4)
    sender_id:UUID
    receiver_id:UUID|None=None
    group_id:UUID|None=None
    content: str=Field(min_length=1)
    timestamp: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))
    status: MessageStatus=Field(default=MessageStatus.SENT)