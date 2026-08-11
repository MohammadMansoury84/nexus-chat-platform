from pydantic import BaseModel


class SignupResponse(BaseModel):
    user_data:dict
    message: str
    
