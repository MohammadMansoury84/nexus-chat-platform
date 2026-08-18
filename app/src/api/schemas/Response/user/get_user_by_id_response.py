from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class GetUserByIdResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    id: UUID
    username: str
    email: EmailStr
