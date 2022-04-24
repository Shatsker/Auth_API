from http import HTTPStatus

from flask import Blueprint, request, make_response

from services.users import UserService


user_router = Blueprint('user_router', __name__)


@user_router.route('/api/v1/users', methods=('GET', ))
def get_users():
    """Получение всех юзеров."""
    data = UserService().get_users()
    return make_response(
        data,
        HTTPStatus.OK,
        {'Content-Type': 'application/json'},
    )


@user_router.route('/api/v1/users', methods=('POST', ))
def create_user():
    """Регистрация нового пользователя."""
    data = UserService().create_user(request.get_json())
    return make_response(
        data,
        HTTPStatus.CREATED,
        {'Content-Type': 'application/json'},
    )
