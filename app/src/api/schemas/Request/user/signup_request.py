from pydantic import BaseModel, ConfigDict


class SignupRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    username: str
    email: str
    password: str
