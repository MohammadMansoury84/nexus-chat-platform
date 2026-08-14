from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GroupMemberResponse(BaseModel):    
    model_config = ConfigDict(
        validate_assignment=True,
    )
    id: UUID
    username: str