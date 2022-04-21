import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv


load_dotenv()

engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'), convert_unicode=True)
db_session = scoped_session(
    sessionmaker(
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from models import users, roles
    Base.metadata.create_all(bind=engine)
