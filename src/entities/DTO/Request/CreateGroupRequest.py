from uuid import UUID

from pydantic import BaseModel


class CreateGroupRequest(BaseModel):
    group_name: str
    creator_id: UUID
