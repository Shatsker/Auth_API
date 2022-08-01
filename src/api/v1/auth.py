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
from services.auth import AuthService, YandexOauthService
from services.users import UserService
from services.utils import get_token_from_header
from core import config

auth_router = Blueprint('auth_router', __name__)

OAUTH_PROVIDERS = {
    'yandex': YandexOauthService,
}


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


@auth_router.route('/api/v1/auth/oauth/<str:provider_name>/link', methods=('POST', ))
def get_oauth_link(provider_name: str):
    """Getting auth link.
        ---
        tags:
          - Auth

        parameters:
          - in: path
            name: provider_name
            required: true
            type: string

        responses:
          200:
            description: Access and refresh tokens
            schema:
              name: authorize_link
              type: string
        """
    provider = OAUTH_PROVIDERS[provider_name]
    return provider.get_auth_link(), HTTPStatus.OK


@auth_router.route('/api/v1/auth/oauth/<string:provider_name>/redirect_uri', methods=('GET', ))
def create_user_from_yandex(provider_name: str):
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
    provider = OAUTH_PROVIDERS[provider_name]

    return provider.create_new_user(code), HTTPStatus.OK
