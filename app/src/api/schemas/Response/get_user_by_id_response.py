from pydantic import BaseModel,EmailStr
from uuid import UUID

class GetUserByIdResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr

    