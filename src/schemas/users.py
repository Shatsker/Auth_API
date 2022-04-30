from uuid import UUID

from pydantic import BaseModel, validator, Field

from .roles import RoleSchema


class BaseUserSchema(BaseModel):
    """Базовая схема для пользователей"""
    login: str = Field(min_length=8, max_length=20)
    email: str = None


class CreateUserSchema(BaseUserSchema):
    """Схема для создания пользователя."""
    password: str

    @validator('password')
    def validate_password(cls, password):
        """Валидация для пароля пользователя."""
        if len(password) < 8:
            raise ValueError('Пароль не может быть меньше 8 символов')
        if password.isdigit():
            raise ValueError('Пароль не может состоять только из цифр.')
        if password.isalpha():
            raise ValueError('Пароль не может состоять только из букв.')
        if password.islower():
            raise ValueError('Пароль не может состоять только из символов нижнего регистра')
        if password.isupper():
            raise ValueError('Пароль не может состоять только из символов верхнего регистра.')

        return password


class UserSchema(BaseUserSchema):
    """Схема для пользователей"""
    roles: list[RoleSchema] = None

    class Config:
        orm_mode = True


class LoginHistorySchema(BaseModel):
    """Схема для истории входа в аккаунт пользователя."""
    user_id: UUID
    user_agent: str
    auth_datetime: str = None
