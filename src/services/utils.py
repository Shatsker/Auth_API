import json
from http import HTTPStatus
from typing import Union

from flask import abort
from flask.wrappers import ResponseBase


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
