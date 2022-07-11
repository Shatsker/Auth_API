from tracing import trace
from models.users import LoginHistory
from services.mixins import CacheRedisMixin, SqlalchemyORMMixin
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
