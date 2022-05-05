import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class Role(Base):
    """Модель для ролей, роль - совокупность прав пользователей."""
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f'<Role: {self.name}>'
