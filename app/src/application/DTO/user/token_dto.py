from pydantic import BaseModel

BEARER_TOKEN_TYPE = "bearer"


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = BEARER_TOKEN_TYPE
