import pydantic,datetime
from pydantic import BaseModel,Field,UUID4
from User import User

class Group(BaseModel):
    id: UUID4=Field(default_factory=UUID4, alias="_id")
    name: str | None=None
    creator_id:UUID4 | None=None
    created_at: str=Field(default_factory=lambda: datetime.now().isoformat())
    members: list[User] = Field(default_factory=list)