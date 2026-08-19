from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from src.core.exceptions.AuthorizationError import AuthorizationError
from src.core.exceptions.DuplicateEmailError import DuplicateEmailError
from src.core.exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.core.exceptions.EmptyDataException import EmptyDataException
from src.core.exceptions.ExpiredAccessTokenError import ExpiredAccessTokenError
from src.core.exceptions.GroupNotFoundError import GroupNotFoundError
from src.core.exceptions.InvalidAccessTokenError import InvalidAccessTokenError
from src.core.exceptions.InvalidCredentialsError import InvalidCredentialsError
from src.core.exceptions.PrivateChatNotFoundError import PrivateChatNotFoundError
from src.core.exceptions.ResponseError import ResponseError
from src.core.exceptions.UserAlreadyInGroupError import UserAlreadyInGroupError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.exceptions.UserNotInGroupError import UserNotInGroupError


class GlobalExceptionHandler:
    def __init__(self, app: FastAPI):
        self.app = app
        self.register_handlers()

    def register_handlers(self):

        # self.app.add_exception_handler(
        #     ApplicationError,self.handle_application_error
        # )
        self.app.add_exception_handler(AuthorizationError, self.handle_authorization_error)

        self.app.add_exception_handler(
            DuplicateEmailError, self.handle_duplicate_email_error
        )

        self.app.add_exception_handler(
            DuplicateUsernameError, self.handle_duplicdate_username_error
        )

        self.app.add_exception_handler(EmptyDataException, self.handle_empty_data_exception)

        self.app.add_exception_handler(
            GroupNotFoundError, self.handle_group_not_found_error
        )

        self.app.add_exception_handler(
            InvalidCredentialsError, self.handle_invalid_credentials_error
        )

        self.app.add_exception_handler(
            PrivateChatNotFoundError, self.handle_private_chat_not_found_error
        )

        self.app.add_exception_handler(ResponseError, self.handle_response_error)

        self.app.add_exception_handler(
            UserAlreadyInGroupError, self.handle_user_already_in_group_error
        )

        self.app.add_exception_handler(UserNotFoundError, self.handle_user_not_found_error)

        self.app.add_exception_handler(
            UserNotInGroupError, self.handle_user_not_in_group_error
        )
        self.app.add_exception_handler(
            InvalidAccessTokenError, self.handle_invalid_access_token_error
        )

        self.app.add_exception_handler(
            ExpiredAccessTokenError, self.handle_expired_access_token_error
        )

        self.app.add_exception_handler(IntegrityError, self.handle_integrity_error)

        self.app.add_exception_handler(OperationalError, self.handle_operational_error)

    # async def handle_application_error(self,request: Request , exc:ApplicationError):
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content={"detail": str(exc)},
    #     )

    async def handle_operational_error(self, request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Database service  is temporarily unavailable"},
        )

    async def handle_integrity_error(self, request: Request, exc: IntegrityError):
        sqlstate = getattr(exc.orig, "sqlstate", None)
        if sqlstate == "23505":
            return JSONResponse(
                status_code=409,
                content={"detail": "resource already exists"},
            )

        if sqlstate == "23503":
            return JSONResponse(
                status_code=409,
                content={"detail": "resource dose not exist"},
            )

        if sqlstate == "23514":
            return JSONResponse(
                status_code=409,
                content={"detail": "database constraint violation "},
            )

        return JSONResponse(
            status_code=500,
            content={"detail": "Database integrity error"},
        )

    async def handle_invalid_access_token_error(
        self, request: Request, exc: InvalidAccessTokenError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    async def handle_expired_access_token_error(
        self, request: Request, exc: ExpiredAccessTokenError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    async def handle_authorization_error(self, request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    async def handle_duplicate_email_error(
        self, request: Request, exc: DuplicateEmailError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    async def handle_duplicdate_username_error(
        self, request: Request, exc: DuplicateUsernameError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    async def handle_empty_data_exception(self, request: Request, exc: EmptyDataException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    async def handle_group_not_found_error(self, request: Request, exc: GroupNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    async def handle_invalid_credentials_error(
        self, request: Request, exc: InvalidCredentialsError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    async def handle_private_chat_not_found_error(
        self, request: Request, exc: PrivateChatNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    async def handle_response_error(self, request: Request, exc: ResponseError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    async def handle_user_already_in_group_error(
        self, request: Request, exc: UserAlreadyInGroupError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    async def handle_user_not_found_error(self, request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    async def handle_user_not_in_group_error(
        self, request: Request, exc: UserNotInGroupError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
