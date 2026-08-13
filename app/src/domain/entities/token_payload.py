from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TokenPayload(BaseModel):
    model_config = ConfigDict(validate_assignment=True,strict=True)
    sub: str
    exp: datetime