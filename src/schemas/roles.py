from flask_marshmallow import Marshmallow


marshmallow = Marshmallow()


class RoleSchema(marshmallow.Schema):
    """Схема для ролей в системе."""
    class Meta:
        fields = ('name', 'permissions')


class PermissionSchema(marshmallow.Schema):
    """Схема для прав в системе."""
    class Meta:
        fields = ('name', )
