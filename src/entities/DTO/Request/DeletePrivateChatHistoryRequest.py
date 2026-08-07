from uuid import UUID

from pydantic import BaseModel


class DeletePrivateChatHistoryRequest(BaseModel):
    user1_id: UUID
    user2_id: UUID
