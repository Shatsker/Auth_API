from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from redis.exceptions import RedisError
from flask_jwt_extended.utils import create_access_token, create_refresh_token

from models.users import LoginHistory
from db.postgres import db_session
from db.redis_db import redis_db
from core import config
from .utils import abort_error


class AbstractTokenizer(ABC):
    """Абстрактный класс для работы с токенами."""

    @abstractmethod
    def get_tokens(self, *args, **kwargs):
        pass

    @abstractmethod
    def refresh_tokens(self, *args, **kwargs):
        pass

    @abstractmethod
    def verify_refresh_token_in_redis(self, *args, **kwargs):
        pass


class JwtTokenizer(AbstractTokenizer):
    """Класс для работы с jwt токенами."""

    def get_tokens(self, identity: str, additional_claims: dict) -> dict:
        """Получение access и refresh токенов для юзера."""
        tokens = {
            'access_token': create_access_token(identity, additional_claims=additional_claims),
            'refresh_token': create_refresh_token(identity, additional_claims=additional_claims),
        }
        # Записываем refresh токен в redis, чтобы поддерживать одноразовость
        try:
            redis_db.setex(
                name=str(identity),
                value=tokens['refresh_token'],
                time=config.JWT_REFRESH_TOKEN_EXPIRES,
            )
        except RedisError:
            abort_error('Ошибка записи токена.')
        finally:
            redis_db.close()

        return tokens

    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict):
        """Проверят присутствие refresh токена в redis'е, а потом возвращает новые токены."""
        is_verified = self.verify_refresh_token_in_redis(sub, refresh_token)

        if is_verified:
            return self.get_tokens(sub, additional_claims)

        abort_error('Токен невалиден.')

    def verify_refresh_token_in_redis(self, key: str, refresh_token: str):
        """Проверят нахождение refresh токена в redis'е"""
        try:
            return redis_db.get(key) == refresh_token.encode('utf-8')
        except RedisError:
            abort_error('Ошибка проверки токена.')
        finally:
            redis_db.close()


class BaseAuthService:
    """Базовый класс для аутентификации."""

    def __init__(self, tokenizer: AbstractTokenizer = JwtTokenizer):
        self.tokenizer = tokenizer()

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
