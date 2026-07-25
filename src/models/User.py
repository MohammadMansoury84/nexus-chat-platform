import pydantic ,datetime
from pydantic import UUID4, BaseModel,Field,EmailStr

class User(BaseModel):
    id: UUID4=Field(default_factory=UUID4, alias="_id")
    username: str |None=None
    email: EmailStr|None=None
    password: str|None=None
    created_at: str=Field(default_factory=lambda: datetime.now().isoformat())


