
from fastapi import APIRouter
from src.api.v1.endpoints.auth_router import auth_router
from src.api.v1.endpoints.user_router import user_router
from src.api.v1.endpoints.message_router import message_router


main_router=APIRouter(
    prefix="/api/v1"
)

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(message_router)

