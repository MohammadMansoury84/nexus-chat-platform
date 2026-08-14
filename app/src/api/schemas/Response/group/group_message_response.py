from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.entities.MessageStatus import MessageStatus




class GroupMessageResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    sender_id: UUID
    group_id: UUID
    content: str
    status: MessageStatus