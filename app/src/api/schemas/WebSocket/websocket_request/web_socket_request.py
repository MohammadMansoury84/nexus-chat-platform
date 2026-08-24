from pydantic import BaseModel, ConfigDict
from src.api.schemas.WebSocket.websocket_action import WebSocketAction


class WebSocketRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    action: WebSocketAction
    data: dict
