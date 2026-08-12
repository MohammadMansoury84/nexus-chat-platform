from uuid import UUID

from pydantic import BaseModel, ConfigDict
from src.domain.entities.GroupMembershipAction import GroupMembershipAction


class GroupMembershipActionDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    action: GroupMembershipAction
    group_id: UUID
    group_name: str
    user_id: UUID
    username: str
