from uuid import UUID
from src.application.service.service_Interface.auth_service import AuthService
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.User import User
from src.core.exceptions.DuplicateEmailError import DuplicateEmailError
from src.core.exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.exceptions.InvalidCredentialsError import InvalidCredentialsError
from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO
from src.domain.repositories_Interface.user_repository import UserRepository


class AuthServiceImpl(AuthService):

    def __init__(self, user_repository: UserRepository) -> None:

        self._user_repository = user_repository
        self.custome_logger = CustomLogger(self.__class__.__name__)


    def signup(self, username: str, email: str, password: str) -> UserDTO:

        self.custome_logger.debug(
            "Attempting to sign up user", username=username, email=email, password=password
        )

        if any(user.username == username for user in self._user_repository.list_all()):
            self.custome_logger.warning("Username already exists", username=username)

            message = "Username already exists."
            raise DuplicateUsernameError(message)

        if any(user.email == email for user in self._user_repository.list_all()):
            self.custome_logger.warning("Email already exists", email=email)

            message = "Email already exists."
            raise DuplicateEmailError(message)

        user = User(username=username, email=email, password=password)

        self._user_repository.add(user=user)

        self.custome_logger.info("User created", username=username, email=email)

        return UserDTO(id=user.id,username=user.username,email=user.email)  

    
    def login(self, username: str, password: str) -> UserDTO :

        self.custome_logger.debug(
            "Attempting to log in user", username=username, password=password
        )

        for user in self._user_repository.list_all():
            if user.username == username and user.password == password:
                self.custome_logger.info("User logged in successfully", username=username)

                return UserDTO(id=user.id,username=user.username,email=user.email)

        self.custome_logger.error("Failed to log in user", username=username)

        raise InvalidCredentialsError(
            "Invalid username or password.")



    def get_other_logged_in_users_for_show(
        self, 
        current_user_id: UUID,
        logged_in_user_ids: set[UUID],
    ) -> list[UserSummaryDTO]:
        return [
            UserSummaryDTO(id=user.id,username=user.username)

            for user in self.get_all_users()
            if user.id in logged_in_user_ids and user.id != current_user_id
        ]

    def get_user_by_id(self, user_id: UUID) -> UserDTO | None:

        user=self._user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found.")

        return UserDTO(id=user.id,username=user.name)

    def get_all_users(self) -> list[UserSummaryDTO]:
        
        return [
            UserSummaryDTO(id=user.id,username=user.username)
            for user in self._user_repository.list_all()
        ]

    

    

    
     

    