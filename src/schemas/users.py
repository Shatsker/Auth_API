from marshmallow import Schema, fields, validate


class BaseUserSchema(Schema):
    """Схема для пользователей"""
    login = fields.Str(required=True, validate=validate.Length(min=8, max=40))
    email = fields.Email()


class CreateUserSchema(BaseUserSchema):
    """Схема создания нового пользователя."""
    password = fields.Str(required=True, validate=validate.Length(min=8, max=70))


class UserSchema(BaseUserSchema):
    """Основная модель пользователя"""
    roles = fields.List(fields.Dict())


class BaseLoginHistorySchema(Schema):
    """Базовая схема для истории входа в аккаунт пользователей."""
    user_agent = fields.Str()
    auth_datetime = fields.DateTime()


class CreateLoginHistory(BaseLoginHistorySchema):
    """Схема для создания истории входа в аккаунт пользователей."""
    user_id = fields.UUID()


class LoginHistorySchema(BaseLoginHistorySchema):
    """Основная схема для истории входа в аккаунт пользователей."""
