from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends


from src.application.service.service_Interface.user_service import UserService
from src.api.schemas.Response.get_user_by_id_response import GetUserByIdResponse
from src.api.schemas.Response.response import Response
from src.api.dependencies.user_service_dependency import get_user_service


user_router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@user_router.get("/{user_id}",response_model=Response[GetUserByIdResponse])
def get_user_by_id(
    user_id : UUID,
    user_service: Annotated[UserService , Depends(get_user_service)]
    )-> Response:
    user=user_service.get_user_by_id(user_id=user_id)
    return Response[GetUserByIdResponse](
        data=GetUserByIdResponse(
            id=user.id,
            username=user.username,
            email=user.email 
        )
    )