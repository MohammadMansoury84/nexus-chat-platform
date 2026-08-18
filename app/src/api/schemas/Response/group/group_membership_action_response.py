from uuid import UUID

from pydantic import BaseModel
from src.domain.entities.GroupMembershipAction import GroupMembershipAction


class GroupMembershipActionResponse(BaseModel):
    action: GroupMembershipAction
    group_id: UUID
    group_name: str
    user_id: UUID
    username: str
