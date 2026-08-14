from uuid import UUID

from src.application.DTO.user.user_dto import UserDTO
from src.application.DTO.user.user_summary_dto import UserSummaryDTO
from src.application.security.password_hasher import PasswordHasher
from src.application.service.service_Interface.auth_service import AuthService
from src.core.exceptions.DuplicateEmailError import DuplicateEmailError
from src.core.exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.core.exceptions.InvalidCredentialsError import InvalidCredentialsError
from src.core.exceptions.UserNotFoundError import UserNotFoundError
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.User import User
from src.domain.repositories_Interface.user_repository import UserRepository
from src.application.security.token_service_interface.token_service import TokenService
from src.application.DTO.user.token_dto import TokenDTO


class AuthServiceImpl(AuthService):
    def __init__(
        self, 
        user_repository: UserRepository, 
        passweord_hasher: PasswordHasher,
        token_service: TokenService
    ) -> None:

        self._user_repository = user_repository
        self._passweord_hasher = passweord_hasher
        self._token_service=token_service
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

        hashed_password = self._passweord_hasher.hash_password(password=password)
        user = User(username=username, email=email, hashed_password=hashed_password)

        self._user_repository.add(user=user)

        self.custome_logger.info("User created", username=username, email=email)

        return UserDTO(id=user.id, username=user.username, email=user.email)
    

    def login(self, username: str, password: str) -> TokenDTO:

        self.custome_logger.debug(
            "Attempting to log in user", username=username, password=password
        )

        user = self._user_repository.get_by_username(username=username)

        if user is None:
            self.custome_logger.error("Failed to log in user", username=username)
            raise InvalidCredentialsError("Invalid username or password.")

        is_password__valid = self._passweord_hasher.verify_passwoed(
            plain_password=password, hashed_password=user.hashed_password
        )

        if not is_password__valid:
            self.custome_logger.error("Failed to log in user", username=username)
            raise InvalidCredentialsError("Invalid username or password.")

        access_token = self._token_service.create_access_token(user_id=user.id)
        
        self._user_repository.add_user_id_to_logged_in_user_ids(user_id=user.id)

       
        self.custome_logger.info("User logged in successfully", username=username)

        return TokenDTO(access_token=access_token,token_type="bearer")


