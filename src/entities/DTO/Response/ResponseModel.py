from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    response_id: UUID = Field(default_factory=uuid4)
    message_type: str = "response"
    request_id: UUID
    status: bool
    data: dict[str, Any] = Field(default_factory=dict)
