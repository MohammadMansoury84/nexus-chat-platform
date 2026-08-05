import asyncio

from src.controllers.AuthController import AuthController
from src.controllers.GroupController import GroupController
from src.controllers.MessageController import MessageController
from src.entities.RequestType import RequestType
from src.repository.GroupRepository import GroupRepository
from src.repository.UserRepository import UserRepository
from src.ServerNetwork.AsyncServer import AsyncServer
from src.ServerNetwork.ConnectionManagement import ConnectionManagement
from src.ServerNetwork.RequestHandler import RequestHandler
from src.ServerNetwork.RequestRouter import RequestRouter
from src.service.AuthService import AuthService
from src.service.GroupService import GroupService
from src.service.MessageService import MessageService

user_repository = UserRepository()
group_repository = GroupRepository()

auth_service = AuthService(user_repository=user_repository)
message_service = MessageService(user_repository=user_repository)
group_service = GroupService(
    user_repository=user_repository, group_repository=group_repository
)


auth_controller = AuthController(auth_service)
message_controller = MessageController(message_service)
group_controller = GroupController(group_service)

connections = ConnectionManagement()
handler = RequestHandler(
    auth_controller,
    message_controller,
    group_controller,
    connections,
)

router = RequestRouter()
router.register_route(RequestType.SINGUP, handler.signup)
router.register_route(RequestType.LOGIN, handler.login)
router.register_route(RequestType.LOGOUT, handler.logout)
router.register_route(RequestType.GET_ALL_USERS_FOR_SHOW_USERS, handler.get_all_users)
router.register_route(RequestType.SEND_PRIVATE_MESSAGE, handler.send_private_message)
router.register_route(RequestType.GET_PRIVATE_CHAT, handler.get_private_chat)
router.register_route(RequestType.CREATE_GROUP, handler.create_group)
router.register_route(RequestType.GET_ALL_GROUPS_FOR_SHOW_USERS, handler.get_all_groups)
router.register_route(RequestType.ADD_USER_TO_GROUP, handler.add_user_to_group)
router.register_route(RequestType.SEND_MESSAGE_TO_GROUP, handler.send_group_message)
router.register_route(RequestType.GET_GROUP_CHAT, handler.get_group_chat)
router.register_route(RequestType.DELETE_GROUP_BY_ID, handler=handler.delete_group_by_id)


server = AsyncServer(
    host="127.0.0.1", port=65432, requestrouter=router, connectionmanagement=connections
)


async def start_server() -> None:
    await server.serve_forever()


try:
    asyncio.run(start_server())
except KeyboardInterrupt:
    print("Server stopped.")  # noqa: T201
