from typing import Union

from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError

from db.postgres import db_session
from models.users import User
from schemas.users import CreateUserSchema, UserSchema
from .base import PassworderAbstract
from .utils import Passworder


class UserService:
    """Бизнес-логика для пользователей."""

    def __init__(self, passworder: PassworderAbstract = Passworder):
        self.passworder = passworder

    def get_users(self) -> str:
        """Получаем всех юзеров из БД."""
        users = User.query.all()
        return UserSchema(many=True).dumps(users)

    def create_user(self, data: dict) -> Union[str, dict]:
        """Создаёт нового пользователя в БД и возвращает его в случае успеха, или ошибку."""
        try:
            user_data = CreateUserSchema().load(data)
            user_data['password'] = self.passworder.hash_password_with_salt(
                user_data['password'],
                user_data['login'],
            )

            new_user = User(**user_data)
            db_session.add(new_user)
            db_session.commit()
        except SQLAlchemyError as err:
            return {'detail': str(err.args)}
        except ValidationError as err:
            return {'detail': err.messages}
        finally:
            db_session.close()

        return CreateUserSchema().dumps(new_user)
