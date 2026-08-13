
from fastapi import APIRouter
from src.api.v1.endpoints.auth_router import auth_router
from src.api.v1.endpoints.user_router import user_router


main_router=APIRouter()

main_router.include_router(auth_router)
main_router.include_router(user_router)

