from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    status: str
