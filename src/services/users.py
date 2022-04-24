from typing import Union

from sqlalchemy.exc import SQLAlchemyError
from marshmallow.exceptions import ValidationError
from passlib.hash import pbkdf2_sha256

from db.postgres import db_session
from models.users import User
from schemas.users import CreateUserSchema, UserSchema


class UserService:
    """Бизнес-логика для пользователей."""

    def get_users(self) -> str:
        """Получаем всех юзеров из БД."""
        users = User.query.all()
        return UserSchema(many=True).dumps(users)

    def create_user(self, data: dict) -> Union[str, dict]:
        """Создаёт нового пользователя в БД и возвращает его в случае успеха, или ошибку."""
        try:
            user_data = CreateUserSchema().load(data)
            user_data['password'] = pbkdf2_sha256.hash(user_data['password'])
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
