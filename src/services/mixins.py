from abc import ABC
from typing import Union
from uuid import UUID

from passlib.hash import pbkdf2_sha256

from base.low_level import SqlalchemyORM
from base.low_level import CacheRedis
from base.abstract import AbstractORM
from base.abstract import AbstractCache
from models.users import User
from services.utils import abort_error
from tracing import trace


class ValidateUserMixin:
    """Миксин для валидации пользователя по паролю."""
    validate_algorithm = pbkdf2_sha256

    @trace
    def _get_validated_user(self, filter_by: dict, password: str) -> Union[User, None]:
        """Проверка существования пользователя, проверка пароля."""
        user = User.query.filter_by(**filter_by).first()

        if not user:
            abort_error('Пользователь не найден.')

        is_password_valid = self.validate_algorithm.verify(
            password,
            user.password,
        )

        if not is_password_valid:
            abort_error('Пароль неверный.')

        return user


class SqlalchemyORMMixin:
    """Миксин для подмешивания orm sqlalchemy."""

    @trace
    def __init__(self, orm: AbstractORM = SqlalchemyORM()):
        super().__init__()
        self.orm = orm


class CacheRedisMixin:
    """Миксин для помешивания редиса."""

    @trace
    def __init__(self, cache_db: AbstractCache = CacheRedis()):
        super().__init__()
        self.cache_db = cache_db


class GetModelMixin(SqlalchemyORMMixin):

    @trace
    def get_by_id(self, model_id, model=None):
        if model is None:
            model = self.model

        obj = self.orm.get_by_id(model, model_id)
        if not obj:
            abort_error('Запись с таким id не существует.')

        return obj


class ListModelMixin(SqlalchemyORMMixin):

    @trace
    def list_all(self):
        objects = self.orm.get_all(self.model)
        return {
            'count': len(objects),
            'source': [self.schema.from_orm(obj).dict() for obj in objects],
        }


class CreateModelMixin(SqlalchemyORMMixin):

    @trace
    def create(self, data: dict):
        new_obj = self.model(**data)
        return self.orm.add_obj(new_obj, self.schema)


class UpdateModelMixin(GetModelMixin, SqlalchemyORMMixin):

    @trace
    def update(self, update_data: dict, obj_id):
        obj = self.get_by_id(obj_id)

        for key, value in update_data.items():
            setattr(obj, key, value)

        return self.orm.add_obj(obj, self.schema)


class DeleteModelMixin(GetModelMixin, SqlalchemyORMMixin):

    @trace
    def delete(self, obj_id):
        obj = self.get_by_id(obj_id)
        self.orm.delete_obj(obj)

        return {'success': True}
