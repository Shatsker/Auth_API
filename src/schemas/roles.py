from marshmallow import Schema, fields


class BaseRoleSchema(Schema):
    """Схема для ролей в системе."""
    name = fields.Str()
    permissions = fields.List(fields.Dict(), required=False)


class CreateRoleSchema(BaseRoleSchema):
    """Схема для создания ролей в системе."""


class RoleSchema(BaseRoleSchema):
    """Основная схема ролей в системе."""


class PermissionSchema(Schema):
    """Схема для прав в системе."""
    name = fields.Str()
