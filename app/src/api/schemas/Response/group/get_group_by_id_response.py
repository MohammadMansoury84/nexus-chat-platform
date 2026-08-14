from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GetGroupByIdResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    group_id: UUID
    group_name: str
    creator_id: UUID