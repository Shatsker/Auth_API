import json
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic.error_wrappers import ValidationError

from services.users import UserService
from schemas.users import CreateUserSchema, ChangePasswordSchema
from services.utils import abort_error

user_router = Blueprint('user_router', __name__)


@user_router.route('/api/v1/users', methods=('GET', ))
@jwt_required()
def get_users(service: UserService = UserService()):
    """Получение всех юзеров.
        ---
        tags:
          - Users

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

        definitions:
          User:
            properties:
              id:
                name: id
                type: integer
                description: User's ID
              email:
                name: email
                type: string
                description: User's email
              login:
                name: login
                type: string
                description: User's login
              roles:
                name: roles
                type: array
                items:
                  $ref: '#/definitions/Role'

          LoginHistory:
            properties:
              auth_datetime:
                name: auth_datetime
                type: date-time
                description: Data of auth
              user_agent:
                name: user_agent
                type: string
                description: User's User-Agent

        responses:
          200:
            description: Got all users
            schema:
              type: array
              items:
                $ref: '#/definitions/User'
        """
    return service.list_all(), HTTPStatus.OK


@user_router.route('/api/v1/users', methods=('POST', ))
def create_user(service: UserService = UserService()):
    """Регистрация нового пользователя.
        ---
        tags:
          - Users

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: formData
            name: login
            type: string
            required: true
          - in: formData
            name: password
            type: string
            required: true

        responses:
          200:
            description: Created user
            schema:
              $ref: '#/definitions/User'
        """
    try:
        data = CreateUserSchema(**request.form)
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.create(data), HTTPStatus.CREATED


@user_router.route('/api/v1/users/<uuid:user_id>/new-password', methods=('POST', ))
@jwt_required()
def change_user_password(user_id: UUID, service: UserService = UserService()):
    """Изменение старого пароля пользователя.
        ---
        tags:
          - Users

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: formData
            name: current_password
            type: string
            required: true
          - in: formData
            name: password
            type: string
            required: true

        responses:
          200:
            description: Updated user
            schema:
              $ref: '#/definitions/User'
        """
    try:
        data = ChangePasswordSchema(**request.form)
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    response = service.change_user_password(user_id, data)

    return response, HTTPStatus.OK


@user_router.route('/api/v1/users/<uuid:user_id>/login-history', methods=('GET', ))
@jwt_required()
def get_login_history_of_user(user_id, service: UserService = UserService()):
    """Получение истории входа в аккаунт пользователя.
        ---
        tags:
          - Users

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: path
            name: user_id
            type: string
            required: true

        responses:
          200:
            description: Got login history
            schema:
              $ref: '#/definitions/LoginHistory'
        """
    if get_jwt_identity() != str(user_id):
        abort_error('Получить информацию о истории входа может только ее владелец.')

    return service.get_login_history_of_user(user_id), HTTPStatus.OK


@user_router.route('/api/v1/users/<uuid:role_id>/roles', methods=('POST', ))
@jwt_required()
def assign_role_to_user(role_id: UUID, service: UserService = UserService()):
    """Назначение роли для пользователя.
        ---
        tags:
          - Users

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

          - in: path
            name: role_id
            type: string
            required: true
          - in: formData
            name: user_id
            type: string
            required: true

        responses:
          200:
            description: Deleted role
            schema:
              name: success
              type: boolean
        """
    user_id = get_jwt_identity()
    response = service.assign_role_to_user(
        role_id=role_id,
        user_id=user_id,
    )
    return response, HTTPStatus.CREATED


@user_router.route('/api/v1/users/<uuid:role_id>/roles', methods=('DELETE', ))
@jwt_required()
def delete_role_from_user(role_id: UUID, service: UserService = UserService()):
    """Удаляет роль у пользователя.
        ---
        tags:
          - Users

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
              name: success
              type: boolean
        """
    user_id = get_jwt_identity()

    response = service.delete_role_from_user(
        role_id=role_id,
        user_id=user_id,
    )

    return response, HTTPStatus.OK
