from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupSummaryDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    group_id: UUID
    group_name: str
