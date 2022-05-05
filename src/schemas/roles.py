from uuid import UUID

from pydantic.main import BaseModel
from pydantic.fields import Field


class BaseRoleSchema(BaseModel):
    """Базовая схема для ролей в системе."""
    name: str = Field(max_length=12)


class CreateRoleSchema(BaseRoleSchema):
    """Схема для создания роли."""


class UpdateRoleSchema(BaseRoleSchema):
    """Схема для создания роли."""


class RoleSchema(BaseRoleSchema):
    """Схема для ролей в системе."""
    id: UUID

    class Config:
        orm_mode = True
