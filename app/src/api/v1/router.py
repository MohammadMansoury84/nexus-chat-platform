from fastapi import APIRouter
from src.api.v1.endpoints.auth_router import auth_router
from src.api.v1.endpoints.group_router import group_router
from src.api.v1.endpoints.message_router import message_router
from src.api.v1.endpoints.user_router import user_router
from src.api.v1.endpoints.websocket_router import websocket_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(message_router)
main_router.include_router(group_router)
main_router.include_router(websocket_router)
