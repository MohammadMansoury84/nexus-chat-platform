from src.application.security.token_service_interface.token_service import TokenService
from src.application.security.password_hasher import PasswordHasher
from src.infrastructure.security.password_hasher_impl import PasswordHasherImpl
from src.infrastructure.security.token_service_implementation.token_service_impl import TokenServiceImpl
from src.core.config.Setting import Setting

settings = Setting()
_passweord_hasher = PasswordHasherImpl()
_token_service=TokenServiceImpl(
    secret_key=settings.jwt_secret_key.get_secret_value(),
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes
    )


def get_passweord_hasher()->PasswordHasher:
    return _passweord_hasher

def get_token_service()->TokenService:
    return _token_service