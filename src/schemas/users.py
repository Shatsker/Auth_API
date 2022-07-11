from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, validator, Field

from tracing import trace
from .roles import RoleSchema


class BaseUserSchema(BaseModel):
    """Базовая схема для пользователей"""
    login: str = Field(min_length=8, max_length=20)
    email: str = None


class PasswordSchemaMixin(BaseModel):
    """Миксин для поля password, который используется в нескольких схемах."""
    password: str

    @trace
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


class CreateUserSchema(BaseUserSchema, PasswordSchemaMixin):
    """Схема для создания пользователя."""


class ChangePasswordSchema(PasswordSchemaMixin):
    """Схема для изменения текущего пароля пользователя."""
    current_password: str


class UserSchema(BaseUserSchema):
    """Схема для пользователей"""
    id: UUID
    roles: list[RoleSchema] = None

    class Config:
        orm_mode = True


class LoginHistorySchema(BaseModel):
    """Схема для истории входа в аккаунт пользователя."""
    user_agent: str
    auth_datetime: datetime = None

    class Config:
        orm_mode = True
