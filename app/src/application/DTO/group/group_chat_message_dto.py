from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupChatMessageDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    sender_id: UUID
    username: str
    content: str
