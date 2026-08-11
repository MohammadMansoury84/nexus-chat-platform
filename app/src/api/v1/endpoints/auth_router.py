from fastapi import APIRouter,Depends
from src.api.schemas.Response.signup_response import SignupResponse
from src.api.schemas.Request.signup_request import SignupRequest
from src.application.service.service_Interface.auth_service import AuthService
from src.api.dependencies.auth_service_dependency import get_auth_service




router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    )


@router.post("/", response_model=SignupResponse)
def signup(signup_request:SignupRequest,service:AuthService=Depends(get_auth_service)):#نوع خروجی 
    user=service.signup(username=signup_request.username,email=signup_request.email,password=signup_request.password)
    return SignupResponse(
        user_data=user.model_dump(),
        message="Account created successfully"
    )


    





