from fastapi import APIRouter, Depends
from src.api.dependencies.auth_service_dependency import get_auth_service
from src.api.schemas.Request.signup_request import SignupRequest
from src.api.schemas.Response.response import Response
from src.api.schemas.Response.signup_response import SignupResponse
from src.application.service.service_Interface.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/", response_model=Response[SignupResponse])
def signup(
    signup_request: SignupRequest, service: AuthService = Depends(get_auth_service)
):  # نوع خروجی
    user = service.signup(
        username=signup_request.username,
        email=signup_request.email,
        password=signup_request.password,
    )
    return Response[SignupResponse](
        data=user.model_dump(), message="Account created successfully"
    )


# @router.post("/",response_model=bool)
# def login(login_request:LoginRequest,service:AuthService=Depends(get_auth_service)):
#     user=service.login(username=login_request.username,password=login_request.password)

#     return True
