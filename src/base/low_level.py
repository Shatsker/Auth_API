from typing import Union
from datetime import timedelta

from redis.exceptions import RedisError
from flask_jwt_extended.utils import create_access_token
from flask_jwt_extended.utils import create_refresh_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

from db.redis_db import redis_db
from db.postgres import db_session
from core import config
from tracing import trace
from services.utils import abort_error
from .abstract import AbstractTokenizer
from .abstract import AbstractCache
from .abstract import AbstractORM


class CacheRedis(AbstractCache):
    """Класс для работы с redis."""

    @trace
    def set_with_expiry(
            self,
            key,
            value,
            time: Union[float, timedelta],
            err_text='Ошибка записи в кеш',
    ) -> None:
        """Устанавливает значение по ключу в редис на время.
            В случае чего выкидывает http ошибку.
        """
        try:
            redis_db.setex(
                name=key,
                value=value,
                time=time,
            )
        except RedisError:
            abort_error(err_text)
        finally:
            redis_db.close()

    @trace
    def get_by_key(self, key, err_text='Ошибка получения кеша.'):
        """Получение значения в redis по ключу.
            В случае чего выкидывает http ошибку.
        """
        try:
            return redis_db.get(name=key)
        except RedisError:
            abort_error(err_text)
        finally:
            redis_db.close()


class JwtTokenizer(AbstractTokenizer):
    """Класс для работы с jwt токенами."""

    @trace
    def __init__(self, cache_db: AbstractCache = CacheRedis()):
        self.cache_db = cache_db

    @trace
    def get_tokens(self, identity: str, additional_claims: dict) -> dict:
        """Получение access и refresh токенов для юзера."""
        tokens = {
            'access_token': create_access_token(identity, additional_claims=additional_claims),
            'refresh_token': create_refresh_token(identity, additional_claims=additional_claims),
        }
        # Записываем refresh токен в кеш, чтобы поддерживать одноразовость
        self.cache_db.set_with_expiry(
            key=str(identity),
            value=tokens['refresh_token'],
            time=config.JWT_REFRESH_TOKEN_EXPIRES,
        )

        return tokens

    @trace
    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict):
        """Проверят присутствие refresh токена в redis'е, а потом возвращает новые токены."""
        is_verified = self.verify_refresh_token_in_redis(sub, refresh_token)

        if is_verified:
            return self.get_tokens(sub, additional_claims)

        abort_error('Токен невалиден.')

    @trace
    def verify_refresh_token_in_redis(self, key: str, refresh_token: str):
        """Проверят нахождение refresh токена в redis'е"""
        err_text = 'Ошибка проверки токена'
        return self.cache_db.get_by_key(key, err_text) == refresh_token.encode()


class SqlalchemyORM(AbstractORM):
    """Класс для работы с ORM sqlalchemy"""

    @trace
    def __init__(self, session=db_session):
        self.session = session

    @trace
    def get_all(self, model):
        return model.query.all()

    @trace
    def get_all_by_filter(self, model, filter_: dict):
        return model.query.filter_by(**filter_).all()

    @trace
    def get_by_id(self, model, id_):
        return model.query.filter_by(id=id_).first()

    @trace
    def add_obj(self, obj, schema=None):
        try:
            self.session.add(obj)
            self.session.commit()
            if schema:
                return schema.from_orm(obj).dict()
        except IntegrityError:
            abort_error('Ошибка записи в БД.')
        finally:
            self.session.close()

    @trace
    def delete_obj(self, obj):
        try:
            self.session.delete(obj)
            self.session.commit()
        finally:
            self.session.close()

    @trace
    def add_to_many_to_many(self, m2m_table, ids: dict):
        try:
            statement = m2m_table.insert().values(**ids)
            self.session.execute(statement)
            self.session.commit()
        finally:
            self.session.close()

    @trace
    def remove_from_many_to_many(self, m2m_table, first_id: tuple, second_id: tuple):
        try:
            attr_first_id = getattr(m2m_table.c, first_id[0])
            attr_second_id = getattr(m2m_table.c, second_id[0])
            statement = delete(m2m_table).where(
                attr_first_id == first_id[1],
                attr_second_id == second_id[1],
            )
            self.session.execute(statement)
            self.session.commit()
        finally:
            self.session.close()
