import json
from http import HTTPStatus
from uuid import UUID

from flask.blueprints import Blueprint
from flask.globals import request
from pydantic.error_wrappers import ValidationError
from flask_jwt_extended import jwt_required

from schemas.roles import CreateRoleSchema
from schemas.roles import UpdateRoleSchema
from services.roles import RoleService
from services.utils import abort_error

role_router = Blueprint('role_router', __name__)


@role_router.route('/api/v1/roles', methods=('GET', ))
@jwt_required()
def get_roles(service: RoleService = RoleService()):
    """Получение всех ролей.
        ---
        tags:
          - Roles

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

        definitions:
          Role:
            properties:
              id:
                name: id
                type: integer
                description: Role's ID
              name:
                name: name
                type: string
                description: Role's name

        responses:
          200:
            description: Got listed roles
            schema:
              type: array
              items:
                $ref: '#/definitions/Role'
        """
    return service.list_all(), HTTPStatus.OK


@role_router.route('/api/v1/roles', methods=('POST', ))
@jwt_required()
def create_role(service: RoleService = RoleService()):
    """Создание новой роли.
        ---
        tags:
          - Roles

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: formData
            name: name
            type: string
            required: true

        responses:
          200:
            description: Created role
            schema:
              $ref: '#/definitions/Role'
        """
    try:
        data = CreateRoleSchema(**request.form).dict()
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.create(data), HTTPStatus.CREATED


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('PATCH', ))
@jwt_required()
def update_role(role_id, service: RoleService = RoleService()):
    """Обновление роли.
        ---
        tags:
          - Roles

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: formData
            name: name
            type: string
            required: true

        responses:
          200:
            description: Updated role
            schema:
              $ref: '#/definitions/Role'
        """
    try:
        data = UpdateRoleSchema(**request.form).dict()
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.update(data, role_id), HTTPStatus.OK


@role_router.route('/api/v1/roles/<uuid:role_id>', methods=('DELETE', ))
@jwt_required()
def delete_role(role_id: UUID, service: RoleService = RoleService()):
    """Удаление роли.
        ---
        tags:
          - Roles

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: path
            name: role_id
            type: string
            required: true

        responses:
          200:
            description: Deleted role
            schema:
              name: message
              type: string
        """
    return service.delete(role_id), HTTPStatus.NO_CONTENT
