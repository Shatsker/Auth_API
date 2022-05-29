from typing import Union
from uuid import UUID

from passlib.hash import pbkdf2_sha256

from models.users import User
from models.users import LoginHistory
from models.users import roles_users
from schemas.users import CreateUserSchema
from schemas.users import LoginHistorySchema
from schemas.users import ChangePasswordSchema
from schemas.users import UserSchema
from . import mixins


class UserService(
    mixins.ValidateUserMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    """Бизнес-логика для пользователей."""
    model = User
    schema = UserSchema

    def create(self, user_data: CreateUserSchema) -> Union[str, dict]:
        """Хешируем пароль пользователя и создаем."""
        user_data.password = pbkdf2_sha256.hash(user_data.password)
        return super().create(user_data.dict())

    def change_user_password(self, user_id: UUID, data: ChangePasswordSchema) -> Union[str, dict]:
        """Обновление пароля пользователя."""
        valid_user = self._get_validated_user({'id': user_id}, data.current_password)
        valid_user.password = pbkdf2_sha256.hash(data.password)

        return self.orm.add_obj(valid_user, self.schema)

    def get_login_history_of_user(self, user_id: UUID) -> dict:
        """Получение истории входа пользователя."""
        login_history = self.orm.get_all_by_filter(LoginHistory, {'user_id': user_id})
        return {
            'count': len(login_history),
            'source': [LoginHistorySchema.from_orm(lh).dict() for lh in login_history]
        }

    def assign_role_to_user(self, role_id, user_id):
        """Добавляет роль пользователя через m2m таблицу, чтобы не делать доп запросов."""
        self.orm.add_to_many_to_many(roles_users, {'role_id': role_id, 'user_id': user_id})
        return {'success': True}

    def delete_role_from_user(self, role_id, user_id):
        """Удаляет роль у пользователя с помощью 3 таблицы для m2m, чтобы не делать доп запросов."""
        self.orm.remove_from_many_to_many(roles_users, ('role_id', role_id), ('user_id', user_id))
        return {'success': True}
