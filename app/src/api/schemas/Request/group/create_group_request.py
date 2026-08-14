from pydantic import BaseModel, ConfigDict


class CreateGroupRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )
    name: str