from schemas.roles import RoleSchema
from models.roles import Role
from . import mixins


class RoleService(
    mixins.UpdateModelMixin,
    mixins.DeleteModelMixin,
    mixins.GetModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    """Бизнес логика для работы с ролями."""
    model = Role
    schema = RoleSchema
