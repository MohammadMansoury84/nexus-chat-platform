from uuid import UUID

from pydantic import BaseModel, EmailStr


class SignupResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
