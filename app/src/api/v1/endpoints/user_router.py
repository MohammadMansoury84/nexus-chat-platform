from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends,status


from src.api.schemas.Response.user_summary_response import UserSummaryResponse
from src.application.service.service_Interface.user_service import UserService
from src.api.schemas.Response.get_user_by_id_response import GetUserByIdResponse
from src.api.schemas.Response.response import Response
from src.api.dependencies.user_service_dependency import get_user_service
from src.api.dependencies.auth_service_dependency import get_current_user_id


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
    dependencies=[Depends(get_current_user_id)],
)


@user_router.get(
        "/by-id//{user_id}",
        response_model=Response[GetUserByIdResponse],
        status_code=status.HTTP_200_OK
        )
def get_user_by_id(
    user_id : UUID,
    user_service: Annotated[UserService , Depends(get_user_service)]
    )-> Response[GetUserByIdResponse]:
    user=user_service.get_user_by_id(user_id=user_id)
    return Response[GetUserByIdResponse](
        data=GetUserByIdResponse(
            id=user.id,
            username=user.username,
            email=user.email 
        )
    )


@user_router.get(
    "/logged-in",
    response_model=Response[list[UserSummaryResponse]],
    status_code=status.HTTP_200_OK,
    )
def get_other_logged_in_users_for_show(
        current_user_id:Annotated[UUID,Depends(get_current_user_id)],
        user_service: Annotated[UserService , Depends(get_user_service)]
    )->Response[list[UserSummaryResponse]]:

    users=user_service.get_other_logged_in_users_for_show(current_user_id=current_user_id)

    return Response[list[UserSummaryResponse]](
        data=[UserSummaryResponse(
                id=user.id,
                username=user.username,
                email=user.email
            ) 
            for user in users
        ]
    )

@user_router.get(
    "/all",
    response_model=Response[list[UserSummaryResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all_users(
    user_service: Annotated[
        UserService,
        Depends(get_user_service)
        ],
    ) -> Response[list[UserSummaryResponse]]:

    users=user_service.get_all_users()

    return Response[list[UserSummaryResponse]](
        data=[UserSummaryResponse(
                id=user.id,
                username=user.username,
                email=user.email
            ) 
            for user in users
        ]
    )
    

     

    