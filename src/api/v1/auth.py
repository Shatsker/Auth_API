from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from services.auth import AuthService

auth_router = Blueprint('auth_router', __name__)


@auth_router.route('/api/v1/login', methods=('POST', ))
def login_user():
    """Аутентификация юзера в системе. Обмен логина и пароля на пару jwt токенов."""
    data = request.get_json()

    response = AuthService().login_user(
        login=data['login'],
        password=data['password'],
        user_agent=request.user_agent.string,
    )

    return response, HTTPStatus.OK


@auth_router.route('/api/v1/refresh', methods=('POST', ))
@jwt_required(refresh=True)
def refresh_tokens():
    """Обновление токенов юзера. Обмен старого refresh на два свежих jwt токена."""
    payload_data = get_jwt()
    old_refresh_token = request.headers.get('Authorization').removeprefix('Bearer ')

    response = AuthService().refresh_tokens(
        sub=payload_data['sub'],
        additional_claims={'roles': payload_data['roles']},
        refresh_token=old_refresh_token,
    )

    return response, HTTPStatus.OK
