from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
)

from src.core.exceptions.ExpiredAccessTokenError import ExpiredAccessTokenError
from src.core.exceptions.InvalidAccessTokenError import InvalidAccessTokenError

from src.application.security.token_service_interface.token_service import TokenService
from src.domain.entities.token_payload import TokenPayload


class TokenServiceImpl(TokenService):

    def __init__(
        self,
        secret_key:str,
        algorithm: str ,
        access_token_expire_minutes: int,
        ):

        self._secret_key=secret_key
        self._algorithm=algorithm
        self._access_token_expire_minutes=access_token_expire_minutes
    


    def create_access_token(self,user_id: UUID)->str:

        expire=datetime.now(timezone.utc)+timedelta(minutes=self._access_token_expire_minutes)

        payload=TokenPayload(
            sub=str(user_id),
            exp=expire
        )

        return jwt.encode(
            payload=payload.model_dump(),
            key=self._secret_key,
            algorithm=self._algorithm
        )



    def decode_token(self,token:str)->UUID:

        try:
            payload=jwt.decode(
                token,
                key=self._secret_key,
                algorithms=[self._algorithm]
            )
        except ExpiredSignatureError as exc:
            raise ExpiredAccessTokenError("Access token has expired."
            )from exc

        except InvalidTokenError as exc:
            raise InvalidAccessTokenError(
                "Invalid access token."
            ) from exc

        subject=payload.get("sub")


        if subject is None:
            raise InvalidAccessTokenError(
            "Invalid access token."
            )


        try:
            return UUID(subject)

        except (ValueError, TypeError) as exc:
            raise InvalidAccessTokenError(
                "Invalid access token."
            ) from exc


        
            



