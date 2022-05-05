from uuid import UUID

from schemas.roles import CreateRoleSchema, RoleSchema, UpdateRoleSchema
from models.roles import Role
from .utils import abort_error
from .base import BaseService


class RoleService(BaseService):
    """Бизнес логика для работы с ролями."""

    def _get_role_by_id(self, role_id):
        return Role.query.filter_by(id=role_id)

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
        role = self._get_role_by_id(role_id).first()

        if not role:
            abort_error('Такой роли нет.')

        for key, value in update_data.items():
            setattr(role, key, value)

        return self._add_obj_to_db(role, RoleSchema)

    def delete_role(self, role_id: UUID) -> None:
        """Удаление роли из базы данных."""
        self._get_role_by_id(role_id).delete()
