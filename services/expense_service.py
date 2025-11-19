"""Expense management service."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .interfaces import ExpenseRepositoryProtocol


class ExpenseService:
    """Encapsulates expense-related operations."""

    def __init__(self, repo_provider: Callable[[], ExpenseRepositoryProtocol]):
        self._repo_provider = repo_provider

    @property
    def repo(self) -> ExpenseRepositoryProtocol:
        return self._repo_provider()

    def list_user_expenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Return all expenses for a user."""
        return self.repo.get_user_expenses(user_id)

    def get_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Return a single expense by id."""
        return self.repo.find_expense(expense_id)

    def create_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist a new expense record."""
        return self.repo.save_expense(data)

    def update_expense(self, expense_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing expense."""
        return self.repo.update_expense(expense_id, updates)

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense."""
        return self.repo.delete_expense(expense_id)

    def summary_by_category(self, user_id: int) -> Dict[str, float]:
        """Return totals grouped by category."""
        return self.repo.summary_by_category(user_id)

    def monthly_totals(self, user_id: int) -> Dict[str, float]:
        """Return totals grouped by year-month."""
        return self.repo.monthly_totals(user_id)


