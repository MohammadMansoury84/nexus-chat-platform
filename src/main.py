
from src.controllers.GroupController import GroupController
from src.controllers.AuthController import AuthController
from src.controllers.MessageController import MessageController
from src.repository.GroupRepository import GroupRepository
from src.repository.UserRepository import UserRepository
from src.service.GroupService import GroupService
from src.service.MessageService import MessageService
from src.service.AuthService import AuthService
from src.view.UserView import UserView




    

user_repository = UserRepository()
group_repository = GroupRepository()

auth_service = AuthService(user_repository=user_repository)
message_service = MessageService(user_repository=user_repository)
group_service = GroupService(user_repository=user_repository, group_repository=group_repository)

        
auth_controller = AuthController(auth_service)
message_controller = MessageController(message_service)
group_controller = GroupController(group_service)

user_view=UserView(auth_controller=auth_controller, message_controller=message_controller, group_controller=group_controller)
user_view.show_Main_menu()






