from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PrivateChatMessageBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: UUID
    chat_id: UUID
    sender_id: UUID
    sender_username: str
    content: str
    status: str
