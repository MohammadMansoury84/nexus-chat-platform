from uuid import UUID

from src.core.CustomeLogger import CustomLogger
from src.entities.User import User
from src.Exceptions.DuplicateEmailError import DuplicateEmailError
from src.Exceptions.DuplicateUsernameError import DuplicateUsernameError
from src.repository.UserRepository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:

        self._user_repository = user_repository
        self.custome_logger = CustomLogger(self.__class__.__name__)

    def signup(self, username: str, email: str, password: str) -> UUID | None:

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

        return user.id

    def login(self, username: str, password: str) -> User | None:

        self.custome_logger.debug(
            "Attempting to log in user", username=username, password=password
        )

        for user in self._user_repository.list_all():
            if user.username == username and user.password == password:
                self.custome_logger.info("User logged in successfully", username=username)

                return user

        self.custome_logger.error("Failed to log in user", username=username)

        return None

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self._user_repository.get_by_id(user_id=user_id)

    def get_other_logged_in_users_for_show(
        self,
        current_user_id: UUID,
        logged_in_user_ids: set[UUID],
    ) -> list[dict]:
        return [
            {
                "id": str(user.id),
                "username": user.username,
            }
            for user in self._user_repository.list_all()
            if user.id in logged_in_user_ids and user.id != current_user_id
        ]

    def get_all_users(self) -> list[User]:
        return self._user_repository.list_all()
