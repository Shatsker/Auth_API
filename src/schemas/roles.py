from pydantic import BaseModel


class PermissionSchema(BaseModel):
    """Схема для прав в системе."""
    name: str


class RoleSchema(BaseModel):
    """Схема для ролей в системе."""
    name: str
    permissions: list[PermissionSchema]
