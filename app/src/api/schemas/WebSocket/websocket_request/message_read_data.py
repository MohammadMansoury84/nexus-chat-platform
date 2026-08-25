from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageReadData(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    chat_partner_id: UUID
