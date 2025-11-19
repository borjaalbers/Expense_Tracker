"""Category management service."""

from __future__ import annotations

from typing import Callable, Dict, List

from .interfaces import CategoryRepositoryProtocol


class CategoryService:
    """Manages user categories with default seeding."""

    def __init__(self, repo_provider: Callable[[], CategoryRepositoryProtocol]):
        self._repo_provider = repo_provider

    @property
    def repo(self) -> CategoryRepositoryProtocol:
        return self._repo_provider()

    def list_categories(self, user_id: int) -> List[Dict[str, str]]:
        return self.repo.list_categories(user_id)

    def add_category(self, user_id: int, name: str) -> Dict[str, str]:
        return self.repo.add_category(user_id, name)

    def delete_category(self, user_id: int, category_id: int) -> bool:
        return self.repo.delete_category(user_id, category_id)


