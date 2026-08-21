from src.application.DTO.user.token_dto import TokenDTO
from src.application.DTO.user.user_dto import UserDTO
from src.application.security.password_hasher import PasswordHasher
from src.application.security.token_service_interface.token_service import TokenService
from src.application.service.service_Interface.auth_service import AuthService
from src.core.exceptions.DuplicateEmailError import DuplicateEmailError
from src.core.exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.core.exceptions.InvalidCredentialsError import InvalidCredentialsError
from src.core.logger.CustomLogger import CustomLogger
from src.domain.entities.User import User
from src.domain.repositories_Interface.redis_online_user_repository import (
    RedisOnlineUserRepository,
)
from src.domain.repositories_Interface.user_repository import UserRepository


class AuthServiceImpl(AuthService):
    def __init__(
        self,
        user_repository: UserRepository,
        passweord_hasher: PasswordHasher,
        token_service: TokenService,
        online_user_repository: RedisOnlineUserRepository,
    ) -> None:

        self._user_repository = user_repository
        self._passweord_hasher = passweord_hasher
        self._token_service = token_service
        self._online_user_repository = online_user_repository
        self.custome_logger = CustomLogger(self.__class__.__name__)

    async def signup(self, username: str, email: str, password: str) -> UserDTO:

        self.custome_logger.debug(
            "Attempting to sign up user", username=username, email=email, password=password
        )

        if await self._user_repository.is_username_used(username=username):
            self.custome_logger.warning("Username already exists", username=username)

            message = "Username already exists."
            raise DuplicateUsernameError(message)

        if await self._user_repository.is_email_used(email=email):
            self.custome_logger.warning("Email already exists", email=email)

            message = "Email already exists."
            raise DuplicateEmailError(message)

        hashed_password = self._passweord_hasher.hash_password(password=password)
        user = User(username=username, email=email, hashed_password=hashed_password)

        await self._user_repository.add(user=user)

        self.custome_logger.info("User created", username=username, email=email)

        return UserDTO(id=user.id, username=user.username, email=user.email)

    async def login(self, username: str, password: str) -> TokenDTO:

        self.custome_logger.debug(
            "Attempting to log in user", username=username, password=password
        )

        user = await self._user_repository.get_by_username(username=username)

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

        await self._online_user_repository.add_online_user(user_id=user.id)

        self.custome_logger.info("User logged in successfully", username=username)

        return TokenDTO(access_token=access_token, token_type="bearer")
