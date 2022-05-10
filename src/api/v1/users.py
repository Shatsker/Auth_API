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
def get_users():
    """Получение всех юзеров."""
    return UserService().get_users(), HTTPStatus.OK


@user_router.route('/api/v1/users', methods=('POST', ))
def create_user():
    """Регистрация нового пользователя."""
    try:
        data = CreateUserSchema(**request.get_json())
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    return UserService().create_user(data), HTTPStatus.CREATED


@user_router.route('/api/v1/users/<uuid:user_id>/new-password', methods=('POST', ))
@jwt_required()
def change_user_password(user_id: UUID):
    """Изменение старого пароля пользователя."""
    try:
        data = ChangePasswordSchema(**request.get_json())
    except ValidationError as err:
        abort_error(json.loads(err.json()))

    response = UserService().change_user_password(
        user_id,
        data,
    )

    return response, HTTPStatus.OK


@user_router.route('/api/v1/users/<uuid:user_id>/login-history', methods=('GET', ))
@jwt_required()
def get_login_history_of_user(user_id):
    """Получение истории входа в аккаунт пользователя."""
    if get_jwt_identity() != str(user_id):
        abort_error('Получить информацию о истории входа может только ее владелец.')

    return UserService().get_login_history_of_user(user_id), HTTPStatus.OK
