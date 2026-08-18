from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupSummaryResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    group_id: UUID
    group_name: str
