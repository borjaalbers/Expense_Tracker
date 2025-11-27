"""
Database setup: SQLAlchemy engine and session factory.

Uses SQLite by default. Configure database URL via DATABASE_URL env var.
"""
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_sqlite_url(path: str) -> str:
    """Return a properly formatted SQLite connection string for an absolute path."""
    absolute = os.path.abspath(path)
    return f"sqlite:///{absolute}"


def _get_database_url() -> str:
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url

    # Prefer a writable persistent volume if one is mounted (e.g., Render disk at /data)
    persistent_dir = os.environ.get("PERSISTENT_DATA_DIR", "/data")
    persistent_path = os.path.join(persistent_dir, "expense_tracker.db")
    if os.path.isdir(persistent_dir) and os.access(persistent_dir, os.W_OK):
        return _build_sqlite_url(persistent_path)

    # Fall back to the repository database file
    default_path = os.path.join(os.path.dirname(__file__), "expense_tracker.db")
    return _build_sqlite_url(default_path)


ENGINE = create_engine(
    _get_database_url(), echo=False, future=True
)

SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_session() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


