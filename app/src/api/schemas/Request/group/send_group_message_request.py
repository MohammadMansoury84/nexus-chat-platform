from pydantic import BaseModel, ConfigDict


class SendGroupMessageRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    content: str