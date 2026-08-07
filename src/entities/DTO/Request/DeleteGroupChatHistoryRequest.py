from uuid import UUID

from pydantic import BaseModel


class DeleteGroupChatHistoryRequest(BaseModel):
    user_id: UUID
    group_id: UUID
