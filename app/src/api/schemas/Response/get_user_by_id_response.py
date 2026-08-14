from pydantic import BaseModel,EmailStr,ConfigDict
from uuid import UUID

class GetUserByIdResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    id:UUID
    username:str
    email:EmailStr

    