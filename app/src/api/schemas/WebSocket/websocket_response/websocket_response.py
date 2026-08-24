from pydantic import BaseModel, ConfigDict


class WebSocketResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    event: str
    data: dict
