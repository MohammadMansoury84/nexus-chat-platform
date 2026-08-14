from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AddUserToGroupRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    user_id: UUID