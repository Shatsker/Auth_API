import json
from http import HTTPStatus
from typing import Union

from flask import abort
from flask.wrappers import ResponseBase

from tracing import trace


@trace
def abort_error(message: str, status: int = HTTPStatus.BAD_REQUEST):
    raise abort(
        JsonResponse({'detail': message}, status=status),
    )


@trace
def get_token_from_header(request):
    return request.headers.get('Authorization').removeprefix('Bearer ')


class JsonResponse(ResponseBase):
    default_mimetype = 'application/json'
    json_module = json

    @trace
    def __init__(self, response: Union[dict, list], status: int = None, *args, **kwargs):
        response = self.json_module.dumps(response)
        super().__init__(response, status, *args, **kwargs)
