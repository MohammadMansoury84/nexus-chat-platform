from src.controllers.UserController import UserController
from src.models.User import User
from src.view.UserView import UserView

UserController = UserController()
UserView=UserView(UserController)



UserView.show_Main_menu()

