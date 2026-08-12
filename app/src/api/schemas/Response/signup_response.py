from pydantic import BaseModel,EmailStr
from uuid import UUID


class SignupResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    
