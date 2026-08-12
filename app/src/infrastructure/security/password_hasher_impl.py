from pwdlib import PasswordHash

from src.application.security.password_hasher import PasswordHasher


class PasswordHasherImpl(PasswordHasher):

    def __init__(self):
        self._hash_password=PasswordHash.recommended()

    def hash_password(self,password:str)->str:
        return self._hash_password.hash(password=password)


    def verify_passwoed(
            self,
            plain_password: str
            ,hashed_password: str
        ,)->bool:
        return self._hash_password.verify(
            password=plain_password,
            hash=hashed_password
            )
        