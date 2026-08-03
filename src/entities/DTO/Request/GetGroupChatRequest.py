from uuid import UUID

from pydantic import BaseModel


class GetGroupChatRequest(BaseModel):
    group_id: UUID
