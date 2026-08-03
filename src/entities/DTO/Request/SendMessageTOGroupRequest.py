from uuid import UUID

from pydantic import BaseModel


class SendMessageToGroupRequest(BaseModel):
    group_id: UUID
    sender_id: UUID
    message_content: str
