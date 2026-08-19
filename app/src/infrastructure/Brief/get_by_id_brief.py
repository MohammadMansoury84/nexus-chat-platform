from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetByIdBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    id: UUID
    email: str
    username: str
