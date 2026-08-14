from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True
    )

    username: str
    password: str
