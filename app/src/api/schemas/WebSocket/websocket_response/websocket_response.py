from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WebSocketResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        strict=True,
    )

    event: str
    request_id: UUID | None = None
    data: dict
