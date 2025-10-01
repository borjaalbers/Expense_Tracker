"""
Pytest configuration and shared fixtures for tests.
"""
import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure we import from parent directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base, User, Expense, Budget, Category
from app import app as flask_app


@pytest.fixture(scope='function')
def test_db_engine():
    """Create a temporary in-memory SQLite database for each test."""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope='function')
def test_db_session(test_db_engine):
    """Provide a transactional database session for each test."""
    SessionLocal = sessionmaker(bind=test_db_engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='function')
def app():
    """Flask app configured for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    return flask_app


@pytest.fixture(scope='function')
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def sample_user(test_db_session):
    """Create a sample user in the test database."""
    from werkzeug.security import generate_password_hash
    user = User(
        username='testuser',
        password_hash=generate_password_hash('testpass123')
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture(scope='function')
def sample_expense(test_db_session, sample_user):
    """Create a sample expense in the test database."""
    from datetime import date
    expense = Expense(
        user_id=sample_user.id,
        amount=50.0,
        category='Food & Dining',
        date=date(2024, 1, 15),
        note='Test expense'
    )
    test_db_session.add(expense)
    test_db_session.commit()
    test_db_session.refresh(expense)
    return expense

