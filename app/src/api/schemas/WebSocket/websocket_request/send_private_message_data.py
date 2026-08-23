from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SendPrivateMessageData(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        strict=True,
    )

    receiver_id: UUID
    content: str
