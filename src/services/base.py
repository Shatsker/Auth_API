from abc import ABC, abstractmethod


class PassworderAbstract(ABC):
    """Абстрактный класс для работы с паролями."""

    @staticmethod
    @abstractmethod
    def hash_password_with_salt(raw_password: str, salt: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def validate_password(password_hash: str, raw_password: str, salt: str) -> str:
        pass
