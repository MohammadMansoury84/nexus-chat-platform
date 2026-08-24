from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SendGroupMessageData(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    group_id: UUID
    content: str
