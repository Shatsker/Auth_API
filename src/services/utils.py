from hashlib import sha256

from .base import PassworderAbstract


class Passworder(PassworderAbstract):
    """Класс для работы с паролями пользователей."""

    @staticmethod
    def hash_password_with_salt(raw_password: str, salt: str) -> str:
        """Хеширует пароль с солью."""
        hashed_password = sha256(raw_password.encode('utf-8') + salt.encode('utf-8'))
        return hashed_password.hexdigest()

    @staticmethod
    def validate_password(password_hash: str, raw_password: str, salt: str) -> str:
        """Валидация роу пароля."""
        if Passworder.hash_password_with_salt(raw_password, salt) == password_hash:
            return True
        return False
