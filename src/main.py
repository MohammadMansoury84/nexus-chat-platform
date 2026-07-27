from src.controllers.UserController import UserController
from src.models.User import User
from src.view.UserView import UserView

userController = UserController()
UserView=UserView(userController)



UserView.show_Main_menu()

