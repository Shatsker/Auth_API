from flask_marshmallow import Marshmallow


marshmallow = Marshmallow()


class UserSchema(marshmallow.Schema):
    """Схема для пользователей"""
    class Meta:
        fields = ('login', 'password', 'roles')


class PersonalUserSchema(marshmallow.Schema):
    """Схема для персональных данных пользователей."""
    class Meta:
        fields = ('user_id', 'phone', 'email', 'first_name', 'middle_name', 'last_name')


class LoginHistorySchema(marshmallow.Schema):
    """Схема для истории входа в аккаунт пользователей."""
    class Meta:
        fields = ('user_id', 'user_agent', 'auth_datetime')
