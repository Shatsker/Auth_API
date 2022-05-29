import json
from http import HTTPStatus
from uuid import UUID

from flask.blueprints import Blueprint
from flask.globals import request
from pydantic.error_wrappers import ValidationError

from schemas.roles import CreateRoleSchema
from schemas.roles import UpdateRoleSchema
from services.roles import RoleService
from services.utils import abort_error

role_router = Blueprint('role_router', __name__)


@role_router.route('/api/v1/roles', methods=('GET', ))
def get_roles(service: RoleService = RoleService()):
    """Получение всех ролей."""
    return service.list_all(), HTTPStatus.OK


@role_router.route('/api/v1/roles', methods=('POST', ))
def create_role(service: RoleService = RoleService()):
    """Создание новой роли."""
    try:
        data = CreateRoleSchema(**request.json).dict()
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.create(data), HTTPStatus.CREATED


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('PATCH', ))
def update_role(role_id, service: RoleService = RoleService()):
    """Обновление существующей роли."""
    try:
        data = UpdateRoleSchema(**request.json).dict()
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.update(data, role_id), HTTPStatus.OK


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('DELETE', ))
def delete_role(role_id: UUID, service: RoleService = RoleService()):
    """Удаление существующей роли."""
    return service.delete(role_id), HTTPStatus.NO_CONTENT
