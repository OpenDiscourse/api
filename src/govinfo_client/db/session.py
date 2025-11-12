"""Database session management."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from govinfo_client.db.models import Base


def get_engine(database_url: str = "sqlite:///govinfo.db"):
    """
    Create and return a database engine.

    Args:
        database_url: Database connection URL

    Returns:
        SQLAlchemy engine
    """
    return create_engine(database_url, echo=False)


def init_db(database_url: str = "sqlite:///govinfo.db") -> None:
    """
    Initialize the database by creating all tables.

    Args:
        database_url: Database connection URL
    """
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)


def get_session(database_url: str = "sqlite:///govinfo.db") -> Generator[Session, None, None]:
    """
    Get a database session.

    Args:
        database_url: Database connection URL

    Yields:
        SQLAlchemy session
    """
    engine = get_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
