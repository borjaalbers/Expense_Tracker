"""Budget calculation and persistence service."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .interfaces import BudgetRepositoryProtocol


class BudgetService:
    """Handles budget CRUD and status calculations."""

    def __init__(self, budget_repo_provider: Callable[[], BudgetRepositoryProtocol]):
        self._repo_provider = budget_repo_provider

    @property
    def budget_repo(self) -> BudgetRepositoryProtocol:
        return self._repo_provider()

    def get_budget(self, user_id: int, month: str) -> Optional[Dict[str, Any]]:
        return self.budget_repo.get_budget(user_id, month)

    def save_budget(self, user_id: int, month: str, limit_amount: float) -> Dict[str, Any]:
        return self.budget_repo.upsert_budget(user_id, month, limit_amount)

    def get_budget_status(self, user_id: int, month: str) -> Dict[str, Any]:
        return self.budget_repo.get_budget_status(user_id, month)


