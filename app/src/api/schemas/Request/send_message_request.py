from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    receiver_id: UUID
    content: str