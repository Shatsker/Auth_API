import json
from http import HTTPStatus
from typing import Union

from flask import abort
from flask.wrappers import ResponseBase


def validate_password(password: str) -> None:
    """Валидация для пароля пользователя."""
    if len(password) < 8:
        raise ValueError('Пароль не может быть меньше 8 символов')
    if password.isdigit():
        raise ValueError('Пароль не может состоять только из цифр.')
    if password.isalpha():
        raise ValueError('Пароль не может состоять только из букв.')
    if password.islower():
        raise ValueError('Пароль не может состоять только из символов нижнего регистра')
    if password.isupper():
        raise ValueError('Пароль не может состоять только из символов верхнего регистра.')


def abort_error(message: str, status: int = HTTPStatus.BAD_REQUEST):
    raise abort(
        JsonResponse({'detail': message}, status=status),
    )


class JsonResponse(ResponseBase):
    default_mimetype = 'application/json'
    json_module = json

    def __init__(self, response: Union[dict, list], status: int = None, *args, **kwargs):
        response = self.json_module.dumps(response)
        super().__init__(response, status, *args, **kwargs)
