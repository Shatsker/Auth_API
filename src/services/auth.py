from datetime import datetime
from typing import Union

from redis.exceptions import RedisError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_refresh_token, create_access_token
from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError

from core import config
from models.users import User, LoginHistory
from schemas.users import CreateLoginHistory
from db.redis_db import redis_db
from db.postgres import db_session


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
        redis_db.setex(
            name=identity,
            value=tokens['refresh_token'],
            time=config.JWT_REFRESH_TOKEN_EXPIRES,
        )
        return tokens


class LoginService(GetTokensMixin):
    """Логика для аутентификации пользователя."""

    def login_user(self, login: str, password: str, user_agent: str) -> Union[dict, None]:
        """Проверка существования юзера, пароля, затем выдача access & refresh токенов."""
        valid_user = self._get_validated_user(login, password)

        if not valid_user:
            return {'detail': 'Неверный логин или пароль'}

        try:
            tokens = self._get_tokens(
                identity=valid_user.login,
                additional_claims={'roles': valid_user.roles},
            )
            self._add_new_entry_to_login_history(
                user_id=valid_user.id,
                user_agent=user_agent,
            )
        except (RedisError, SQLAlchemyError):
            return {'detail': 'Ошибка входа.'}
        except ValidationError as err:
            return {'detail': err.messages}
        finally:
            db_session.close()
            redis_db.close()

        return tokens

    @staticmethod
    def _get_validated_user(login: str, password: str) -> Union[User, None]:
        """Проверка существования пользователя, проверка пароля."""
        user = User.query.filter_by(login=login).first()

        if not user:
            return

        is_password_valid = pbkdf2_sha256.verify(
            password,
            user.password,
        )

        if is_password_valid:
            return user

    @staticmethod
    def _add_new_entry_to_login_history(user_id: str, user_agent: str) -> None:
        """Добавляем запись в историю входов пользователя."""
        data = CreateLoginHistory().load(
            {
                'user_agent': user_agent,
                'user_id': user_id,
            },
        )
        login_history = LoginHistory(**data)

        db_session.add(login_history)
        db_session.commit()


class TokenService(GetTokensMixin):
    """Логика для работы с токенами."""

    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict) -> dict:
        """Проверят присутствие refresh токена в redis'е, а потом возвращает новые токены."""
        try:
            is_verified = self._verify_refresh_token_in_redis(sub, refresh_token)

            if is_verified:
                return self._get_tokens(sub, additional_claims)
        except RedisError:
            return {'detail': 'Ошибка проверки токена.'}
        finally:
            redis_db.close()

        return {'detail': 'Токен невалиден.'}

    @staticmethod
    def _verify_refresh_token_in_redis(key: str, refresh_token: str):
        """Проверят нахождение refresh токена в redis'е"""
        return redis_db.get(key) == refresh_token.encode('utf-8')
