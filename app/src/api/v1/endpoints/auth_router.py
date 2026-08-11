from fastapi import APIRouter,Depends

from src.api.schemas.Request import SignupRequest
from src.application.service.service_Interface.auth_service import AuthService
from src.api.dependencies.auth_service_dependency import get_auth_service




router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    )


@router.post("/", response_model=None)
def signup():#نوع خروجی 
    pass





