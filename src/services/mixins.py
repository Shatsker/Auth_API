from typing import Union
from uuid import UUID

from passlib.hash import pbkdf2_sha256

from models.users import User
from services.utils import abort_error


class ValidateUserMixin:
    """Миксин для валидации пользователя по паролю."""
    validate_algorithm = pbkdf2_sha256

    def _get_validated_user(self, filter_by: dict, password: str) -> Union[User, None]:
        """Проверка существования пользователя, проверка пароля."""
        user = User.query.filter_by(**filter_by).first()

        if not user:
            abort_error('Пользователь не найден.')

        is_password_valid = self.validate_algorithm.verify(
            password,
            user.password,
        )

        if not is_password_valid:
            abort_error('Пароль неверный.')

        return user


class GetUserMixin:
    """Миксин для получения пользователя."""

    def _get_user_by_id(self, user_id: UUID) -> User:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            abort_error('Пользователь не найден.')

        return user
