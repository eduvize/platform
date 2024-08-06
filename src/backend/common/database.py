from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import get_database_connection_string


connection_string = get_database_connection_string()
engine = create_engine(connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Context = declarative_base()

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Retrieves an ephemeral session for database operations

    Yields:
        Generator[Session, None, None]: The session object
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()