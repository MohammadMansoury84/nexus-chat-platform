from typing import Annotated

from fastapi import APIRouter, Depends,status
from src.api.dependencies.auth_service_dependency import get_auth_service
from src.api.schemas.Request.signup_request import SignupRequest
from src.api.schemas.Response.response import Response
from src.api.schemas.Response.signup_response import SignupResponse
from src.application.service.service_Interface.auth_service import AuthService
from src.api.schemas.Request.login_request import LoginRequest
from src.api.schemas.Response.login_response import LoginResponse

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@auth_router.post(
        "/signup", 
        response_model=Response[SignupResponse],
        status_code=status.HTTP_201_CREATED,
        )
def signup(
    signup_request: SignupRequest, 
    auth_service: Annotated[AuthService , Depends(get_auth_service)]
)->Response[SignupResponse]: 
    user = auth_service.signup(
        username=signup_request.username,
        email=signup_request.email,
        password=signup_request.password,
    )
    return Response[SignupResponse](
        data=SignupResponse(
            id=user.id,
            username=user.username,
            email=user.email
        ),
        message="Account created successfully"
    )


@auth_router.post(
        "/login",
        response_model=Response[LoginResponse],
        status_code=status.HTTP_200_OK,
        )
def login(
    login_request:LoginRequest, 
    auth_service: Annotated[AuthService , Depends(get_auth_service)]
)->Response[LoginResponse] : 
    token=auth_service.login(
        username=login_request.username,
        password=login_request.password
    )
    return Response[LoginResponse](
        data=LoginResponse(
            token_type=token.token_type,
            access_token=token.access_token
        ),
        message="User logged in successfully"
    )








    