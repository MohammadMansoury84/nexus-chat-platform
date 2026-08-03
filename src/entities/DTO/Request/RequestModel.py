from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.entities.RequestType import RequestType


class RequestModel(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    request_type: RequestType
    data: dict[str, Any] = Field(default_factory=dict)
