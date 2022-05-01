from typing import Union

from .mixins import ValidateUserMixin
from .utils import abort_error
from .base import BaseAuthService


class AuthService(BaseAuthService, ValidateUserMixin):
    """Логика для аутентификации пользователя."""

    def login_user(self, login: str, password: str, user_agent: str) -> Union[dict, None]:
        """Проверка существования юзера, пароля, затем выдача access & refresh токенов."""
        valid_user = self._get_validated_user({'login': login}, password)

        if not valid_user:
            abort_error('Неверный логин или пароль')

        tokens = self.tokenizer.get_tokens(
            identity=valid_user.id,
            additional_claims={'roles': valid_user.roles},
        )

        self._add_new_entry_to_login_history(
            user_id=valid_user.id,
            user_agent=user_agent,
        )

        return tokens

    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict):
        return self.tokenizer.refresh_tokens(
            sub,
            refresh_token,
            additional_claims,
        )
