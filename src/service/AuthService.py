from src.repository.UserRepository import UserRepository
from src.entities.User import User
from src.core.CustomeLogger import CustomLogger
from src.Exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
)
from uuid import UUID


class AuthService:

    def __init__(self, user_repository: UserRepository) -> None:

        self._user_repository = user_repository
        self.custome_logger= CustomLogger(self.__class__.__name__)
    


    def signup(self, username: str, email: str, password: str)->UUID | None:

        
    
        self.custome_logger.debug("Attempting to sign up user", username=username, email=email, password=password)



        if any(user.username == username for user in self._user_repository.list_all()):
            

            self.custome_logger.warning(f"Username already exists", username=username)

            raise DuplicateUsernameError("Username already exists.")

        if any(user.email == email for user in self._user_repository.list_all()):

            self.custome_logger.warning(f"Email already exists", email=email)

            raise DuplicateEmailError("Email already exists.")

        user = User(username=username,email=email,password=password)

        self._user_repository.add(user=user)

        self.custome_logger.info("User created", username=username, email=email)

        return user.id

    
    def login(self, username: str, password: str)-> User | None:
        
        self.custome_logger.debug("Attempting to log in user", username=username, password=password)
        
        for user in self._user_repository.list_all():
            if user.username == username and user.password == password:

                self.custome_logger.info("User logged in successfully", username=username)

                return user
            
        self.custome_logger.error("Failed to log in user", username=username)

        return None

    def get_user_by_id(self, user_id: UUID)-> User |None :
        return self._user_repository.get_by_id(user_id=user_id)


    def get_all_users_for_show_users(self)->list[dict]:
        user_list = []
        for user in self._user_repository.list_all():
            user_list.append(f"User ID: {user.id}, Username: {user.username}")
        return user_list

    def get_all_users(self)->list[User]:
        return self._user_repository.list_all()

    



    

    


    

    