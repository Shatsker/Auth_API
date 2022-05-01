from typing import Union

from passlib.hash import pbkdf2_sha256

from models.users import User


class ValidateUserMixin:
    """Миксин для валидации пользователя по паролю."""
    validate_algorithm = pbkdf2_sha256

    def _get_validated_user(self, filter_by: dict, password: str) -> Union[User, None]:
        """Проверка существования пользователя, проверка пароля."""
        user = User.query.filter_by(**filter_by).first()

        if not user:
            return

        is_password_valid = self.validate_algorithm.verify(
            password,
            user.password,
        )

        if is_password_valid:
            return user
