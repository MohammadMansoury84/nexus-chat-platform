from uuid import UUID

from pydantic import BaseModel


class LeaveGroupRequest(BaseModel):
    user_id: UUID
    group_id: UUID
