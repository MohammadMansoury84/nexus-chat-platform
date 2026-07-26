from src.controllers.UserController import UserController
from src.models.User import User

UserController = UserController()
print (1)
user1: User = print(UserController.signup("user2", "user1@example.com", "password1"))
print (2)
print(login_user := UserController.login("user2", "password1"))
print (3)

