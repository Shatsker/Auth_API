import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base
from .users import roles_users


class Role(Base):
    """Модель для ролей, роль - совокупность прав пользователей."""
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    users = relationship('User', secondary=roles_users, back_populates='roles')

    def __repr__(self):
        return f'<Role: {self.name}>'
