from typing import Union
from uuid import UUID
from http import HTTPStatus

from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256

from db.postgres import db_session
from models.users import User, LoginHistory
from schemas.users import UserSchema, CreateUserSchema, LoginHistorySchema
from .mixins import ValidateUserMixin
from .utils import validate_password, abort_error


class UserService(ValidateUserMixin):
    """Бизнес-логика для пользователей."""

    def get_users(self) -> str:
        """Получаем всех юзеров из БД."""
        users = User.query.all()
        return {
            'count': len(users),
            'source': [UserSchema.from_orm(user).dict() for user in users],
        }

    def create_user(self, user_data: CreateUserSchema) -> Union[str, dict]:
        """Создаёт нового пользователя в БД и возвращает его в случае успеха, или ошибку."""
        user_data.password = pbkdf2_sha256.hash(user_data.password)
        new_user = User(**user_data.dict())

        try:
            db_session.add(new_user)
            db_session.commit()
            return UserSchema.from_orm(new_user).dict()
        except IntegrityError as err:
            abort_error(err.args[0])
        finally:
            db_session.close()

    def update_user_password(self, user_id: UUID, current_password: str, new_password: str) -> Union[str, dict]:
        """Обновление пароля юзера."""
        valid_user = self._get_validated_user({'id': user_id}, current_password)

        if valid_user:
            try:
                validate_password(new_password)
                valid_user.password = pbkdf2_sha256.hash(new_password)
                db_session.add(valid_user)
                db_session.commit()
                return UserSchema.from_orm(valid_user).dict()
            except IntegrityError as err:
                abort_error(err.args[0], HTTPStatus.NOT_MODIFIED)
            except ValueError as err:
                abort_error(err.args[0])
            finally:
                db_session.close()

        abort_error('Пароль неверный.')

    def get_login_history_of_user(self, user_id: UUID) -> dict:
        """Получение истории входа пользователя."""
        login_history = LoginHistory.query.filter_by(user_id=user_id).all()
        return {
            'count': len(login_history),
            'source': [LoginHistorySchema.from_orm(lh).dict() for lh in login_history]
        }
