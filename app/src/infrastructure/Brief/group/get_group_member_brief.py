from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetGroupMemberBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    member_id: UUID
    member_username: str
