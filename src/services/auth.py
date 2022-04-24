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


class AuthService:
    """Логика для аутентификации пользователя."""

    def login_user(self, login: str, password: str, user_agent: str) -> Union[dict, None]:
        """Проверка существования юзера, пароля, затем выдача access & refresh токенов."""
        valid_user = self._get_validated_user(login, password)

        if not valid_user:
            return {'detail': 'Неверный логин или пароль'}

        tokens = self._get_tokens(valid_user)

        try:
            # Записываем refresh токен в redis, чтобы поддерживать одноразовость
            redis_db.setex(
                name=str(valid_user.id),
                value=tokens['refresh_token'],
                time=config.JWT_REFRESH_TOKEN_EXPIRES,
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
    def _get_tokens(valid_user: User) -> dict:
        """Получение access и refresh токенов для юзера."""
        additional_claims_for_access = {
            'roles': valid_user.roles,
        }

        return {
            'access_token': create_access_token(valid_user.login, additional_claims=additional_claims_for_access),
            'refresh_token': create_refresh_token(valid_user.login),
        }

    @staticmethod
    def _add_new_entry_to_login_history(user_id: str, user_agent: str) -> None:
        """Добавляем запись в историю входов пользователя."""
        data = CreateLoginHistory().load(
            {
                'user_agent': user_agent,
                'user_id': user_id,
                'auth_datetime': str(datetime.now()),
            },
        )
        login_history = LoginHistory(**data)

        db_session.add(login_history)
        db_session.commit()
