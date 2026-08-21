from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ListAllBrief(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: UUID
    email: str
    username: str
    created_at: datetime
