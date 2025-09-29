"""
Database setup: SQLAlchemy engine and session factory.

Uses SQLite by default. Configure database URL via DATABASE_URL env var.
"""
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _get_database_url() -> str:
    # Default to SQLite file in project directory
    default_path = os.path.join(os.path.dirname(__file__), "expense_tracker.db")
    return os.environ.get("DATABASE_URL", f"sqlite:///{default_path}")


ENGINE = create_engine(
    _get_database_url(), echo=False, future=True
)

SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_session() -> Iterator["Session"]:
    from sqlalchemy.orm import Session  # local import for type checker

    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


