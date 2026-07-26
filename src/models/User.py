from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: uuid4=Field(default_factory=uuid4)
    username: str=Field(min_length=4,max_length=20)
    email: EmailStr
    password: str=Field(min_length=6,max_length=150)
    created_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))


