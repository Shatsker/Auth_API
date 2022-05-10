from typing import Union
from uuid import UUID
from http import HTTPStatus

from passlib.hash import pbkdf2_sha256

from models.users import User, LoginHistory
from schemas.users import UserSchema, CreateUserSchema, LoginHistorySchema, ChangePasswordSchema
from .mixins import ValidateUserMixin
from .base import BaseService


class UserService(BaseService, ValidateUserMixin):
    """Бизнес-логика для пользователей."""

    def get_users(self) -> dict:
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

        return self._add_obj_to_db(new_user, UserSchema)

    def change_user_password(self, user_id: UUID, data: ChangePasswordSchema) -> Union[str, dict]:
        """Обновление пароля пользователя."""
        valid_user = self._get_validated_user({'id': user_id}, data.current_password)
        valid_user.password = pbkdf2_sha256.hash(data.password)

        return self._add_obj_to_db(valid_user, UserSchema, HTTPStatus.NOT_MODIFIED)

    def get_login_history_of_user(self, user_id: UUID) -> dict:
        """Получение истории входа пользователя."""
        login_history = LoginHistory.query.filter_by(user_id=user_id).all()
        return {
            'count': len(login_history),
            'source': [LoginHistorySchema.from_orm(lh).dict() for lh in login_history]
        }
