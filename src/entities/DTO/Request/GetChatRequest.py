from uuid import UUID

from pydantic import BaseModel


class GetChatRequest(BaseModel):
    user1_id: UUID
    user2_id: UUID
