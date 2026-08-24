from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupMessageDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID
    sender_id: UUID
    group_id: UUID
    content: str
    status: str
