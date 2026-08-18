from pydantic import BaseModel, ConfigDict


class LoginResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    access_token: str
    token_type: str
