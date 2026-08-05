from uuid import UUID

from pydantic import BaseModel


class DeleteGroupByIdRequest(BaseModel):
    group_id: UUID
