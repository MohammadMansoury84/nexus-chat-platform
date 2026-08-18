from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SendMessageResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    id: UUID
    sender_username: str
    receiver_username: str
    content: str
    status: str
