from uuid import UUID

from pydantic import BaseModel,EmailStr,ConfigDict

class UserSummaryResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    id:UUID
    username:str
    email:EmailStr
    