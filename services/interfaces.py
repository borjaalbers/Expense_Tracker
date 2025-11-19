"""Protocol definitions for repository abstractions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class UserRepositoryProtocol(Protocol):
    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        ...

    def find_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        ...

    def save_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        ...


class ExpenseRepositoryProtocol(Protocol):
    def get_user_expenses(self, user_id: int) -> List[Dict[str, Any]]:
        ...

    def find_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
        ...

    def save_expense(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def update_expense(self, expense_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ...

    def delete_expense(self, expense_id: int) -> bool:
        ...

    def summary_by_category(self, user_id: int) -> Dict[str, float]:
        ...

    def monthly_totals(self, user_id: int) -> Dict[str, float]:
        ...


class BudgetRepositoryProtocol(Protocol):
    def get_budget(self, user_id: int, month: str) -> Optional[Dict[str, Any]]:
        ...

    def upsert_budget(self, user_id: int, month: str, limit_amount: float) -> Dict[str, Any]:
        ...

    def get_budget_status(self, user_id: int, month: str) -> Dict[str, Any]:
        ...


class CategoryRepositoryProtocol(Protocol):
    def list_categories(self, user_id: int) -> List[Dict[str, Any]]:
        ...

    def add_category(self, user_id: int, name: str) -> Dict[str, Any]:
        ...

    def delete_category(self, user_id: int, category_id: int) -> bool:
        ...


