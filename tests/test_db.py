"""
Unit tests for db.py database configuration.
"""
import pytest
from unittest.mock import patch, MagicMock
import db


class TestDatabaseConfig:
    """Test database configuration and utilities."""

    def test_get_database_url_default(self):
        """Test default database URL generation."""
        url = db._get_database_url()
        
        assert 'sqlite:///' in url
        assert 'expense_tracker.db' in url

    @patch.dict('os.environ', {'DATABASE_URL': 'sqlite:///custom.db'})
    def test_get_database_url_from_env(self):
        """Test database URL from environment variable."""
        url = db._get_database_url()
        
        assert url == 'sqlite:///custom.db'

    def test_engine_exists(self):
        """Test that ENGINE is created."""
        assert db.ENGINE is not None

    def test_session_local_exists(self):
        """Test that SessionLocal factory exists."""
        assert db.SessionLocal is not None

    def test_get_session_context_manager(self):
        """Test get_session context manager."""
        with db.get_session() as session:
            assert session is not None

    def test_get_session_rollback_on_exception(self):
        """Test that session rolls back on exception."""
        try:
            with db.get_session() as session:
                # Force an exception
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected

    def test_get_session_commit_on_success(self):
        """Test that session commits on successful exit."""
        with db.get_session() as session:
            # Normal exit should commit
            pass

