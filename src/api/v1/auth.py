from http import HTTPStatus

from flask import Blueprint
from flask import make_response, jsonify, request

from services.auth import AuthService


auth_router = Blueprint('auth_router', __name__)


@auth_router.route('/api/v1/login', methods=('POST', ))
def login_user():
    data = request.get_json()
    tokens = AuthService().login_user(
        login=data['login'],
        password=data['password'],
        user_agent=request.user_agent.string,
    )

    if tokens.get('detail'):
        return make_response(tokens, HTTPStatus.BAD_REQUEST)

    return make_response(
        jsonify(tokens),
        HTTPStatus.OK,
    )
