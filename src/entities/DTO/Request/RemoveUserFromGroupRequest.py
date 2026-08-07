from uuid import UUID

from pydantic import BaseModel


class RemoveUserFromGroupRequest(BaseModel):
    group_id: UUID
    user_id: UUID
