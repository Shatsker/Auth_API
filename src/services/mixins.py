from typing import Union

from flask_jwt_extended import create_refresh_token, create_access_token
from passlib.hash import pbkdf2_sha256
from redis.exceptions import RedisError

from core import config
from db.redis_db import redis_db
from models.users import User
from .utils import abort_error


class GetTokensMixin:
    """Миксин для получения access & refresh токенов."""

    @staticmethod
    def _get_tokens(identity: str, additional_claims: dict) -> dict:
        """Получение access и refresh токенов для юзера."""
        tokens = {
            'access_token': create_access_token(identity, additional_claims=additional_claims),
            'refresh_token': create_refresh_token(identity, additional_claims=additional_claims),
        }
        # Записываем refresh токен в redis, чтобы поддерживать одноразовость
        try:
            redis_db.setex(
                name=identity,
                value=tokens['refresh_token'],
                time=config.JWT_REFRESH_TOKEN_EXPIRES,
            )
        except RedisError:
            abort_error('Ошибка записи токена.')
        finally:
            redis_db.close()

        return tokens


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
