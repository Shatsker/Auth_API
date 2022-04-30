import json
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from pydantic.error_wrappers import ValidationError

from services.users import UserService
from schemas.users import CreateUserSchema
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


@user_router.route('/api/v1/users/<uuid:user_id>/new_password', methods=('POST', ))
@jwt_required()
def update_user_password(user_id: UUID):
    """Изменение старого пароля пользователя."""
    current_password = request.json['current_password']
    new_password = request.json['new_password']

    response = UserService().update_user_password(
        user_id,
        current_password,
        new_password,
    )

    return response, HTTPStatus.OK
