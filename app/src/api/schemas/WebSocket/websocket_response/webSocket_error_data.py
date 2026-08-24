from typing import Any

from pydantic import BaseModel, ConfigDict


class WebSocketErrorData(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        strict=True,
    )

    code: str
    message: str
    details: list[dict[str, Any]] | None = None
