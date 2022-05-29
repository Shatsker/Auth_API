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
    """Получение всех юзеров."""
    return service.list_all(), HTTPStatus.OK


@user_router.route('/api/v1/users', methods=('POST', ))
def create_user(service: UserService = UserService()):
    """Регистрация нового пользователя."""
    try:
        data = CreateUserSchema(**request.get_json())
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return service.create(data), HTTPStatus.CREATED


@user_router.route('/api/v1/users/<uuid:user_id>/new-password', methods=('POST', ))
@jwt_required()
def change_user_password(user_id: UUID, service: UserService = UserService()):
    """Изменение старого пароля пользователя."""
    try:
        data = ChangePasswordSchema(**request.get_json())
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    response = service.change_user_password(
        user_id,
        data,
    )

    return response, HTTPStatus.OK


@user_router.route('/api/v1/users/<uuid:user_id>/login-history', methods=('GET', ))
@jwt_required()
def get_login_history_of_user(user_id, service: UserService = UserService()):
    """Получение истории входа в аккаунт пользователя."""
    if get_jwt_identity() != str(user_id):
        abort_error('Получить информацию о истории входа может только ее владелец.')

    return service.get_login_history_of_user(user_id), HTTPStatus.OK


@user_router.route('/api/v1/users/<uuid:role_id>/roles', methods=('POST', ))
@jwt_required()
def assign_role_to_user(role_id: UUID, service: UserService = UserService()):
    """Назначение роли для пользователя."""
    user_id = get_jwt_identity()
    response = service.assign_role_to_user(
        role_id=role_id,
        user_id=user_id,
    )
    return response, HTTPStatus.CREATED


@user_router.route('/api/v1/users/<uuid:role_id>/roles', methods=('DELETE', ))
@jwt_required()
def delete_role_from_user(role_id: UUID, service: UserService = UserService()):
    """Удаляет роль у пользователя."""
    user_id = get_jwt_identity()
    response = service.delete_role_from_user(
        role_id=role_id,
        user_id=user_id,
    )
    return response, HTTPStatus.OK
