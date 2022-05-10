import json
from http import HTTPStatus
from uuid import UUID

from flask.blueprints import Blueprint
from flask.globals import request
from pydantic.error_wrappers import ValidationError

from schemas.roles import CreateRoleSchema, UpdateRoleSchema
from services.roles import RoleService
from services.utils import abort_error

role_router = Blueprint('role_router', __name__)


@role_router.route('/api/v1/roles', methods=('GET', ))
def get_roles():
    """Получение всех ролей."""
    return RoleService().get_roles(), HTTPStatus.OK


@role_router.route('/api/v1/roles', methods=('POST', ))
def create_role():
    """Создание новой роли."""
    try:
        data = CreateRoleSchema(**request.json)
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return RoleService().create_role(data), HTTPStatus.CREATED


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('PATCH', ))
def update_role(role_id):
    """Обновление существующей роли."""
    try:
        data = UpdateRoleSchema(**request.json)
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return RoleService().update_role(data, role_id), HTTPStatus.OK


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('DELETE', ))
def delete_role(role_id: UUID):
    """Удаление существующей роли."""
    RoleService().delete_role(role_id)
    return 'OK', HTTPStatus.NO_CONTENT


@role_router.route('/api/v1/roles/<uuid:role_id>/assign-role', methods=('POST', ))
def assign_role_to_user(role_id: UUID):
    """Назначение роли для пользователя."""
    user_id = request.json.get('user_id')
    response = RoleService().assign_role_to_user(
        role_id=role_id,
        user_id=user_id,
    )
    return response, HTTPStatus.CREATED


@role_router.route('/api/v1/roles/<uuid:role_id>/take-away-role', methods=('POST', ))
def take_away_role_from_user(role_id: UUID):
    user_id = request.json.get('user_id')
    response = RoleService().take_away_role_from_user(
        role_id=role_id,
        user_id=user_id,
    )
    return response, HTTPStatus.OK
