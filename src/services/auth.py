from typing import Union
from datetime import timedelta

from .mixins import ValidateUserMixin
from base.base import BaseAuthService


class AuthService(BaseAuthService, ValidateUserMixin):
    """Логика для аутентификации пользователя."""

    def login_user(self, login: str, password: str, user_agent: str) -> Union[dict, None]:
        """
        Проверка существования юзера, пароля,
        затем выдача пары access & refresh токена.
        """
        valid_user = self._get_validated_user(
            {'login': login},
            password,
        )

        tokens = self.tokenizer.get_tokens(
            identity=valid_user.id,
            additional_claims={'roles': [role.name for role in valid_user.roles]},
        )

        self._add_new_entry_to_login_history(
            user_id=valid_user.id,
            user_agent=user_agent,
        )

        return tokens

    def logout_user(self, jti: str, time: timedelta):
        """
        Добавляет access токен в редис, чтобы знать,
        что этот токен уже устарел т.к. был в запросе на логаут.
        """
        self.cache_db.set_with_expiry(jti, '', time)
        return {
            'success': True,
            'expiry_time': time.seconds,
        }

    def refresh_tokens(self, sub: str, refresh_token: str, additional_claims: dict):
        """
        Обновляет токены пользователя, взамен на старый refresh токен.
        Поддерживается одноразовость refresh токена,
        чтобы им можно было воспользоваться только один раз
        """
        return self.tokenizer.refresh_tokens(
            sub,
            refresh_token,
            additional_claims,
        )
