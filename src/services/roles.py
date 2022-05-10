from uuid import UUID

from schemas.roles import CreateRoleSchema, RoleSchema, UpdateRoleSchema
from schemas.users import UserSchema
from models.roles import Role
from db.postgres import db_session
from .utils import abort_error
from .base import BaseService
from .mixins import GetUserMixin


class RoleService(BaseService, GetUserMixin):
    """Бизнес логика для работы с ролями."""

    def _get_role_by_id(self, role_id: UUID) -> Role:
        """Получение роли по id или вызов ошибки, если роль отсутствует."""
        role = Role.query.filter_by(id=role_id).first()

        if not role:
            abort_error('Роль не найдена.')

        return role

    def get_roles(self):
        """Получение всех ролей из базы данных."""
        roles = Role.query.all()
        return {
            'count': len(roles),
            'source': [RoleSchema.from_orm(role).dict() for role in roles],
        }

    def create_role(self, data: CreateRoleSchema) -> dict:
        """Создание новой роли."""
        new_role = Role(**data.dict())
        return self._add_obj_to_db(new_role, RoleSchema)

    def update_role(self, data: UpdateRoleSchema, role_id: UUID) -> dict:
        """Обновление роли."""
        update_data = data.dict()
        role = self._get_role_by_id(role_id)

        for key, value in update_data.items():
            setattr(role, key, value)

        return self._add_obj_to_db(role, RoleSchema)

    def delete_role(self, role_id: UUID) -> None:
        """Удаление роли из базы данных."""
        role = self._get_role_by_id(role_id)

        try:
            db_session.delete(role)
            db_session.commit()
        except Exception as err:
            db_session.rollback()
            raise err
        finally:
            db_session.close()

    def assign_role_to_user(self, role_id: UUID, user_id: UUID) -> dict:
        """Назначает роль для пользователя, если у него ее нет."""
        role = self._get_role_by_id(role_id)
        user = self._get_user_by_id(user_id)

        if role in user.roles:
            abort_error('Пользователь уже имеет эту роль.')

        user.roles.append(role)

        return self._add_obj_to_db(user, UserSchema)

    def take_away_role_from_user(self, role_id: UUID, user_id: UUID) -> dict:
        """Отбирает роль у пользователя, если она есть."""
        role = self._get_role_by_id(role_id)
        user = self._get_user_by_id(user_id)

        if role not in user.roles:
            abort_error('У пользователя нет этой роли.')

        user.roles.remove(role)

        return self._add_obj_to_db(user, UserSchema)
