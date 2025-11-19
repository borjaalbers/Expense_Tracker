"""Authentication and user management service."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .interfaces import UserRepositoryProtocol


class AuthService:
    """Single-responsibility service for user authentication concerns."""

    def __init__(self, repo_provider: Callable[[], UserRepositoryProtocol]):
        self._repo_provider = repo_provider

    @property
    def repo(self) -> UserRepositoryProtocol:
        return self._repo_provider()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a user record by identifier."""
        return self.repo.find_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch a user by username."""
        return self.repo.find_user_by_username(username)

    def create_user(self, username: str, password_hash: str) -> Dict[str, Any]:
        """Persist a new user with the provided password hash."""
        return self.repo.save_user({"username": username, "password_hash": password_hash})


