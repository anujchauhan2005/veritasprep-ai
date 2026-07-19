"""
db/session.py
---------------
Sets up the database connection. Uses SQLite by default (a single file
on disk, zero setup needed) but DATABASE_URL can be swapped to point
at PostgreSQL for a more production-like setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yields a database session, and always closes it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
