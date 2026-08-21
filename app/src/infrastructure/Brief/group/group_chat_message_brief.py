from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupChatMessageBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: UUID
    group_id: UUID
    sender_id: UUID
    sender_username: str
    content: str
    created_at: datetime
