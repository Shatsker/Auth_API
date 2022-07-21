import uuid
import datetime

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Table,
    Text,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base

roles_users = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete="CASCADE")),
    Column('role_id', ForeignKey('roles.id')),
    keep_existing=True
)


def create_partitions_for_users(target, connection, **kwargs) -> None:
    """Creating partition by login_history """
    values = ((0, 1000000), (1000000, 2000000), (2000000, 3000000))

    for value in values:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS "users_{}_{}" 
            PARTITION OF "users" 
            FOR VALUES FROM ('{}') TO ('{}')
            """.format(value[0], value[1], value[0], value[1])
        )


class User(Base):
    """Основная модель юзера."""
    __tablename__ = 'users'
    __table_args__ = (
        {
            'postgresql_partition_by': 'RANGE (id)',
            'listeners': [('after_create', create_partitions_for_users)],
        }
    )

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, index=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    roles = relationship('Role', secondary=roles_users, cascade='all,delete', back_populates="users")

    def __repr__(self):
        return f'<User: {self.login}>'


class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    auth_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    user_agent = Column(Text)

    def __repr__(self):
        return f'<LoginHistory {self.user_id}:{self.auth_datetime }>'
