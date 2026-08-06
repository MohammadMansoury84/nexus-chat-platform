from uuid import UUID

from pydantic import BaseModel


class ShowGroupMembersRequest(BaseModel):
    user_id: UUID
    group_id: UUID
