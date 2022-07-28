import json
import os

import requests
import uuid
from http import HTTPStatus

from werkzeug.exceptions import HTTPException
from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from rauth import OAuth2Service

from schemas.users import CreateUserSchema
from services.auth import AuthService
from services.users import UserService
from services.utils import get_token_from_header
from core import config

auth_router = Blueprint('auth_router', __name__)


@auth_router.route('/api/v1/login', methods=('POST',))
def login_user(service: AuthService = AuthService()):
    """Аутентификация юзера в системе. Обмен логина и пароля на пару jwt токенов.
        ---
        tags:
          - Auth

        parameters:
          - in: formData
            name: username
            type: string
            required: true
          - in: formData
            name: password
            type: string
            required: true

        definitions:
          Tokens:
            type: object
            properties:
              access_token:
                name: access_token
                type: string
                description: Access token for accessing to server
              refresh_token:
                name: refresh_token
                type: string
                description: Refresh token for refreshing tokens

        responses:
          200:
            description: Access and refresh tokens
            schema:
              $ref: '#/definitions/Tokens'
        """
    data = request.form

    response = service.login_user(
        login=data['username'],
        password=data['password'],
        user_agent=request.user_agent.string,
    )

    return response, HTTPStatus.OK


@auth_router.route('/api/v1/logout', methods=('POST',))
@jwt_required()
def logout_user(service: AuthService = AuthService()):
    """Выход пользователя из системы. Добавляет access токен в redis.
        ---
        tags:
          - Auth

        parameters:
          - in: header
            name: access_token
            type: string
            required: true

        responses:
          200:
            description: Access and refresh tokens
            schema:
              name: message
              type: string
        """
    jti = get_jwt()['jti']

    response = service.logout_user(
        jti=jti,
        time=config.JWT_ACCESS_TOKEN_EXPIRES,
    )

    return response, HTTPStatus.OK


@auth_router.route('/api/v1/refresh', methods=('POST',))
@jwt_required(refresh=True)
def refresh_tokens(service: AuthService = AuthService()):
    """Обновление токенов юзера. Обмен старого refresh на два свежих jwt токена.
        ---
        tags:
          - Auth

        parameters:
          - in: header
            name: access_token
            type: string
            required: true
          - in: header
            name: refresh_token
            type: string
            required: true

        responses:
          200:
            description: Access and refresh tokens
            schema:
              $ref: '#/definitions/Tokens'
        """
    payload_data = get_jwt()
    old_refresh_token = get_token_from_header(request)

    response = service.refresh_tokens(
        sub=payload_data['sub'],
        additional_claims={'roles': payload_data['roles']},
        refresh_token=old_refresh_token,
    )

    return response, HTTPStatus.OK


@auth_router.route('/api/v1/auth/yandex/link', methods=('POST', ))
def get_auth_yandex_link():
    """Getting auth link.
        ---
        tags:
          - Auth

        responses:
          200:
            description: Access and refresh tokens
            schema:
              name: authorize_link
              type: string
        """
    yandex_service = OAuth2Service(
        client_id=os.getenv('YANDEX_CLIENT_ID'),
        client_secret=os.getenv('YANDEX_CLIENT_SECRET'),
        name=os.getenv('yandex'),
        authorize_url=os.getenv('YANDEX_AUTHORIZE_URL'),
        access_token_url=os.getenv('YANDEX_ACCESS_TOKEN_URL'),
        base_url=os.getenv('YANDEX_BASE_URL'),
    )

    params = {
        'scope': 'login:email',
        'response_type': 'code',
        'redirect_uri': os.getenv('YANDEX_REDIRECT_URI'),
    }

    return {"authorize_link": yandex_service.get_authorize_url(**params)}, HTTPStatus.OK


@auth_router.route('/api/v1/auth/yandex/redirect_uri', methods=('GET', ))
def create_user_from_yandex():
    """Getting auth link.
        ---
        tags:
          - Auth

        parameters:
          - in: query
            name: code
            required: true

        responses:
          200:
            description: Access and refresh tokens
            schema:
              name: authorize_link
              type: string
        """
    code = request.args['code']

    yandex_service = OAuth2Service(
        client_id=os.getenv('YANDEX_CLIENT_ID'),
        client_secret=os.getenv('YANDEX_CLIENT_SECRET'),
        name=os.getenv('yandex'),
        authorize_url=os.getenv('YANDEX_AUTHORIZE_URL'),
        access_token_url=os.getenv('YANDEX_ACCESS_TOKEN_URL'),
        base_url=os.getenv('YANDEX_BASE_URL'),
    )

    access_token = yandex_service.get_access_token(
        data={'code': code, 'grant_type': 'authorization_code'},
        decoder=json.loads,
    )

    with requests.get(
            url='https://login.yandex.ru/info',
            headers={'Authorization': f'OAuth {access_token}'},
    ) as response:
        login = response.json()['login']
        data = CreateUserSchema(login=login, password=str(uuid.uuid4()))

    try:
        tokens = AuthService().login_user(data.login, data.password, 'oauth')
    except HTTPException:
        UserService().create(data)
        tokens = AuthService().login_user(data.login, data.password, 'oauth')

    return {'tokens': tokens}, HTTPStatus.OK
