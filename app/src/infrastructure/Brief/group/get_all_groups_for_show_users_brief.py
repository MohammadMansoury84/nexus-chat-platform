from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetAllGroupsForShowUsersBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    group_id: UUID
    group_name: str
