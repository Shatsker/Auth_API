import uuid

from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


association_table = Table(
    'roles_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id')),
    Column('permission_id', ForeignKey('permissions.id')),
)


class Role(Base):
    """Модель для ролей, роль - совокупность прав пользователей."""
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    permissions = relationship('Permission', secondary=association_table)

    def __repr__(self):
        return f'<Role: {self.name}>'


class Permission(Base):
    """Модель для прав пользователя."""
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Permission: {self.name}>'
