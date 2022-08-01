import json
import requests
import uuid
from rauth import OAuth2Service
from werkzeug.exceptions import HTTPException

from tracing import trace
from models.users import LoginHistory
from services.mixins import CacheRedisMixin, SqlalchemyORMMixin
from services.auth import AuthService
from services.users import UserService
from core import config
from schemas.users import CreateUserSchema
from .abstract import AbstractTokenizer
from .low_level import JwtTokenizer


class BaseAuthService(CacheRedisMixin, SqlalchemyORMMixin):
    """Базовый класс для аутентификации."""

    @trace
    def __init__(self, tokenizer: AbstractTokenizer = JwtTokenizer()):
        super().__init__()
        self.tokenizer = tokenizer

    @trace
    def _add_new_entry_to_login_history(self, user_id: str, user_agent: str) -> None:
        """Добавляем запись в историю входа пользователя."""
        login_history = LoginHistory(user_id=user_id, user_agent=user_agent)
        self.orm.add_obj(login_history)


class BaseOAuthService(BaseAuthService):

    client_id = None
    client_secret = None
    name = None
    authorize_url = None
    access_token_url = None
    base_url = None
    redirect_uri = None
    scope = None
    info_url = None

    def __init__(self):
        super().__init__()

        self.provider = OAuth2Service(
            client_id=self.client_id,
            client_secret=self.client_secret,
            name=self.name,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url,
        )

    def get_auth_link(self) -> dict:
        params = {'scope': self.scope, 'response_type': 'code', 'redirect_uri': self.redirect_uri}
        return {"authorize_link": self.provider.get_authorize_url(**params)}

    def create_new_user(self, code):
        access_token = self.provider.get_access_token(
            data={'code': code, 'grant_type': 'authorization_code'},
            decoder=json.loads,
        )

        with requests.get(
                url=self.info_url,
                headers={'Authorization': f'OAuth {access_token}'},
        ) as response:
            login = response.json()['login']
            data = CreateUserSchema(login=login, password=str(uuid.uuid4()))

        try:
            tokens = AuthService().login_user(data.login, data.password, 'oauth')
        except HTTPException:
            UserService().create(data)
            tokens = AuthService().login_user(data.login, data.password, 'oauth')

        return {'tokens': tokens}
