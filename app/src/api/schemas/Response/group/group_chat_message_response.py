from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupChatMessageResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    sender_id: UUID
    username: str
    content: str
