from uuid import UUID

from pydantic import BaseModel,EmailStr
class UserSummaryResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    