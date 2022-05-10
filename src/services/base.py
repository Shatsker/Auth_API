from abc import ABC, abstractmethod
from http import HTTPStatus

from pydantic.main import BaseModel
from sqlalchemy.exc import IntegrityError
from redis.exceptions import RedisError
from flask_jwt_extended.utils import create_access_token, create_refresh_token

from models.users import LoginHistory
from db.postgres import db_session, Base
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


class BaseService:
    """Базовый класс для сервисов."""

    def _add_obj_to_db(self, obj: Base, schema: BaseModel = None, err_status: int = HTTPStatus.BAD_REQUEST):
        """Добавляет объект модели в db и возвращает его схему."""
        try:
            db_session.add(obj)
            db_session.commit()
            if schema:
                return schema.from_orm(obj).dict()
        except IntegrityError as err:
            db_session.rollback()
            abort_error(err.args[0], err_status)
        except Exception as err:
            db_session.rollback()
            raise err
        finally:
            db_session.close()


class BaseAuthService(BaseService):
    """Базовый класс для аутентификации."""

    def __init__(self, tokenizer: AbstractTokenizer = JwtTokenizer):
        self.tokenizer = tokenizer()

    def _add_new_entry_to_login_history(self, user_id: str, user_agent: str) -> None:
        """Добавляем запись в историю входа пользователя."""
        login_history = LoginHistory(user_id=user_id, user_agent=user_agent)
        self._add_obj_to_db(login_history)
