from abc import ABC, abstractmethod


class AbstractTokenizer(ABC):
    """Абстрактный класс для работы с токенами."""

    @abstractmethod
    def get_tokens(self, *args, **kwargs):
        pass

    @abstractmethod
    def refresh_tokens(self, *args, **kwargs):
        pass

    @abstractmethod
    def verify_refresh_token_in_redis(self, *args, **kwargs):
        pass


class AbstractCache(ABC):
    """Абстрактный класс для работы с кешем."""

    @abstractmethod
    def set_with_expiry(self, key, value, time, err_text=None) -> None:
        pass

    @abstractmethod
    def get_by_key(self, key, err_text=None):
        pass


class AbstractORM(ABC):
    """Абстрактный класс для работы с ORM."""

    @abstractmethod
    def __init__(self, session):
        """Инициализация подключения к БД."""
        pass

    @abstractmethod
    def get_all(self, model):
        """Получение всех записей."""
        pass

    @abstractmethod
    def get_all_by_filter(self, model, filter_: dict):
        """Получение всех записей по фильтру."""
        pass

    @abstractmethod
    def get_by_id(self, model, id_):
        """Получение записи по id."""
        pass

    @abstractmethod
    def add_obj(self, obj, schema=None):
        """Добавление объекта в БД."""
        pass

    @abstractmethod
    def delete_obj(self, obj):
        """Удаление объекта из БД."""
        pass

    @abstractmethod
    def add_to_many_to_many(self, m2m_table, ids: dict):
        """Добавление записей(айдишников) в m2m таблицу."""
        pass

    @abstractmethod
    def remove_from_many_to_many(self, *args, **kwargs):
        """Удаление айдишников из m2m таблицы."""
        pass
