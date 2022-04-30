from typing import Union

from redis.exceptions import RedisError
from sqlalchemy.exc import IntegrityError

from models.users import LoginHistory
from db.redis_db import redis_db
from db.postgres import db_session
from .mixins import GetTokensMixin, ValidateUserMixin
from .utils import abort_error


class LoginService(GetTokensMixin, ValidateUserMixin):
    """Логика для аутентификации пользователя."""

    def login_user(self, login: str, password: str, user_agent: str) -> Union[dict, None]:
        """Проверка существования юзера, пароля, затем выдача access & refresh токенов."""
        valid_user = self._get_validated_user({'login': login}, password)

        if not valid_user:
            abort_error('Неверный логин или пароль')

        tokens = self._get_tokens(
            identity=valid_user.login,
            additional_claims={'roles': valid_user.roles},
        )

        self._add_new_entry_to_login_history(
            user_id=valid_user.id,
            user_agent=user_agent,
        )

        return tokens

    @staticmethod
    def _add_new_entry_to_login_history(user_id: str, user_agent: str) -> None:
        """Добавляем запись в историю входов пользователя."""
        try:
            login_history = LoginHistory(
                user_id=user_id,
                user_agent=user_agent,
            )
            db_session.add(login_history)
            db_session.commit()
        except IntegrityError:
            abort_error('Ошибка целостности данных.')
        finally:
            db_session.close()


class TokenService(GetTokensMixin):
    """Логика для работы с токенами."""

    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict) -> dict:
        """Проверят присутствие refresh токена в redis'е, а потом возвращает новые токены."""
        is_verified = self._verify_refresh_token_in_redis(sub, refresh_token)

        if is_verified:
            return self._get_tokens(sub, additional_claims)

        abort_error('Токен невалиден.')

    @staticmethod
    def _verify_refresh_token_in_redis(key: str, refresh_token: str):
        """Проверят нахождение refresh токена в redis'е"""
        try:
            return redis_db.get(key) == refresh_token.encode('utf-8')
        except RedisError:
            abort_error('Ошибка проверки токена.')
        finally:
            redis_db.close()
