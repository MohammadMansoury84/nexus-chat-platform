from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetByUserNameBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    id: UUID
    hashed_password: str
