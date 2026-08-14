from uuid import UUID

from pydantic import BaseModel, ConfigDict,EmailStr


class UserSummaryDTO(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True, strict=True)
    id: UUID
    username: str
    email:EmailStr
 