from pydantic import BaseModel


class loginResponse(BaseModel):
    tohen_type: str
    token: str
