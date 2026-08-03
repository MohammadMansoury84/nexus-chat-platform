from uuid import UUID

from pydantic import BaseModel


class AddUserToGroupRequest(BaseModel):
    group_id: UUID
    creator_id: UUID
    user_id: UUID
