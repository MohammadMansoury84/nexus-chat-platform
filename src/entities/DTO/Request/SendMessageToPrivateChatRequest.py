from uuid import UUID

from pydantic import BaseModel


class SendMessageToPrivateChatRequest(BaseModel):
    sender_id: UUID
    receiver_id: UUID
    message_content: str
