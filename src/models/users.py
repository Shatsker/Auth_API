import uuid
import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


association_table = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('role_id', ForeignKey('roles.id')),
)


class User(Base):
    """Основная модель юзера без персональных данных, они в таблице personal_users."""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)
    login = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    roles = relationship('Role', secondary=association_table)

    def __repr__(self):
        return f'<User: {self.login}>'


class PersonalUser(Base):
    """Модель персональных данных юзера."""
    __tablename__ = 'personal_users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True)
    phone = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)


class LoginHistory(Base):
    """Модель для логирования входов в аккаунт пользователя."""
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user_agent = Column(String, nullable=False)
    auth_datetime = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return f'<LoginHistory: {self.user_agent}>'
