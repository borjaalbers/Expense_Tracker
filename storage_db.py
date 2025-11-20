from __future__ import annotations

from datetime import date
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db import get_session
from models import User, Expense, Budget, Category
from config import Config

TModel = TypeVar("TModel")
TResult = TypeVar("TResult")


class BaseRepository:
    """Generic repository utilities for SQLAlchemy models."""

    model: Type[TModel]

    @classmethod
    def _execute(cls, fn: Callable[[Session], TResult]) -> TResult:
        with get_session() as session:
            return fn(session)

    @classmethod
    def _get(cls, session: Session, obj_id: int) -> Optional[TModel]:
        return session.get(cls.model, obj_id)

    @staticmethod
    def _scalar_one(session: Session, stmt):
        return session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _scalars(session: Session, stmt):
        return session.scalars(stmt).all()


class UserRepository(BaseRepository):
    model = User

    @staticmethod
    def _to_dict(user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash,
        }

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        def _run(session: Session):
            users = cls._scalars(session, select(cls.model).order_by(cls.model.id.asc()))
            return [cls._to_dict(user) for user in users]

        return cls._execute(_run)

    @classmethod
    def find_by_username(cls, username: str) -> Optional[Dict[str, Any]]:
        def _run(session: Session):
            user = cls._scalar_one(session, select(cls.model).where(cls.model.username == username))
            return cls._to_dict(user) if user else None

        return cls._execute(_run)

    @classmethod
    def find_by_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        def _run(session: Session):
            user = cls._get(session, user_id)
            return cls._to_dict(user) if user else None

        return cls._execute(_run)

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        def _run(session: Session):
            obj = cls.model(username=data["username"], password_hash=data["password_hash"])
            session.add(obj)
            session.flush()
            return cls._to_dict(obj)

        return cls._execute(_run)


class ExpenseRepository(BaseRepository):
    model = Expense

    @staticmethod
    def _to_dict(exp: Expense) -> Dict[str, Any]:
        return {
            "id": exp.id,
            "user_id": exp.user_id,
            "amount": float(exp.amount),
            "category": exp.category,
            "date": exp.date.isoformat() if exp.date else None,
            "note": exp.note,
        }

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        def _run(session: Session):
            records = cls._scalars(session, select(cls.model).order_by(cls.model.id.asc()))
            return [cls._to_dict(exp) for exp in records]

        return cls._execute(_run)

    @classmethod
    def list_for_user(cls, user_id: int) -> List[Dict[str, Any]]:
        def _run(session: Session):
            stmt = (
                select(cls.model)
                .where(cls.model.user_id == user_id)
                .order_by(cls.model.date.desc(), cls.model.id.desc())
            )
            records = cls._scalars(session, stmt)
            return [cls._to_dict(exp) for exp in records]

        return cls._execute(_run)

    @classmethod
    def find(cls, expense_id: int) -> Optional[Dict[str, Any]]:
        def _run(session: Session):
            exp = cls._get(session, expense_id)
            return cls._to_dict(exp) if exp else None

        return cls._execute(_run)

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        def _run(session: Session):
            date_obj = date.fromisoformat(data["date"]) if data.get("date") else None
            obj = cls.model(
                user_id=data["user_id"],
                amount=data["amount"],
                category=data["category"],
                date=date_obj,
                note=data["note"],
            )
            session.add(obj)
            session.flush()
            return cls._to_dict(obj)

        return cls._execute(_run)

    @classmethod
    def update(cls, expense_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        def _run(session: Session):
            exp = cls._get(session, expense_id)
            if not exp:
                return None
            for field, value in updates.items():
                if field == "date" and value:
                    setattr(exp, field, date.fromisoformat(value))
                else:
                    setattr(exp, field, value)
            session.flush()
            return cls._to_dict(exp)

        return cls._execute(_run)

    @classmethod
    def delete(cls, expense_id: int) -> bool:
        def _run(session: Session):
            exp = cls._get(session, expense_id)
            if not exp:
                return False
            session.delete(exp)
            return True

        return cls._execute(_run)

    @classmethod
    def summary_by_category(cls, user_id: int) -> Dict[str, float]:
        def _run(session: Session):
            rows = session.execute(
                select(cls.model.category, func.sum(cls.model.amount))
                .where(cls.model.user_id == user_id)
                .group_by(cls.model.category)
            ).all()
            return {cat or "Uncategorized": float(total or 0.0) for cat, total in rows}

        return cls._execute(_run)

    @classmethod
    def monthly_totals(cls, user_id: int) -> Dict[str, float]:
        def _run(session: Session):
            rows = session.execute(
                select(func.strftime("%Y-%m", cls.model.date), func.sum(cls.model.amount))
                .where(cls.model.user_id == user_id)
                .group_by(func.strftime("%Y-%m", cls.model.date))
            ).all()
            return {ym or "": float(total or 0.0) for ym, total in rows}

        return cls._execute(_run)


class BudgetRepository(BaseRepository):
    model = Budget

    @staticmethod
    def _to_dict(obj: Budget) -> Dict[str, Any]:
        return {
            "id": obj.id,
            "user_id": obj.user_id,
            "month": obj.month,
            "limit_amount": float(obj.limit_amount),
        }

    @classmethod
    def get_for_month(cls, user_id: int, month: str) -> Optional[Dict[str, Any]]:
        def _run(session: Session):
            obj = cls._scalar_one(
                session, select(cls.model).where(cls.model.user_id == user_id, cls.model.month == month)
            )
            return cls._to_dict(obj) if obj else None

        return cls._execute(_run)

    @classmethod
    def upsert(cls, user_id: int, month: str, limit_amount: float) -> Dict[str, Any]:
        def _run(session: Session):
            obj = cls._scalar_one(
                session, select(cls.model).where(cls.model.user_id == user_id, cls.model.month == month)
            )
            if obj:
                obj.limit_amount = limit_amount
            else:
                obj = cls.model(user_id=user_id, month=month, limit_amount=limit_amount)
                session.add(obj)
            session.flush()
            return cls._to_dict(obj)

        return cls._execute(_run)


class CategoryRepository(BaseRepository):
    model = Category

    @staticmethod
    def _to_dict(cat: Category) -> Dict[str, Any]:
        return {"id": cat.id, "name": cat.name, "user_id": cat.user_id}

    @classmethod
    def _ensure_defaults(cls, session: Session, user_id: int) -> None:
        existing = session.execute(select(cls.model).where(cls.model.user_id == user_id)).scalars().all()
        if existing:
            return
        for name in Config.DEFAULT_CATEGORIES:
            session.add(cls.model(user_id=user_id, name=name))

    @classmethod
    def ensure_defaults(cls, user_id: int) -> None:
        def _run(session: Session):
            cls._ensure_defaults(session, user_id)

        cls._execute(_run)

    @classmethod
    def list_for_user(cls, user_id: int) -> List[Dict[str, Any]]:
        def _run(session: Session):
            cats = (
                session.execute(
                    select(cls.model).where(cls.model.user_id == user_id).order_by(cls.model.name.asc())
                )
                .scalars()
                .all()
            )
            return [{"id": cat.id, "name": cat.name} for cat in cats]

        return cls._execute(_run)

    @classmethod
    def add(cls, user_id: int, name: str) -> Dict[str, Any]:
        def _run(session: Session):
            existing = cls._scalar_one(
                session, select(cls.model).where(cls.model.user_id == user_id, cls.model.name == name)
            )
            if existing:
                return {"id": existing.id, "name": existing.name}
            obj = cls.model(user_id=user_id, name=name.strip())
            if not obj.name:
                raise ValueError("name required")
            session.add(obj)
            session.flush()
            return {"id": obj.id, "name": obj.name}

        return cls._execute(_run)

    @classmethod
    def delete(cls, user_id: int, category_id: int) -> bool:
        def _run(session: Session):
            obj = cls._get(session, category_id)
            if not obj or obj.user_id != user_id:
                return False
            session.delete(obj)
            return True

        return cls._execute(_run)



# --- Users ---
def get_all_users() -> List[Dict[str, Any]]:
    """Return all users as dictionaries."""
    return UserRepository.list_all()


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Return user data searched by username."""
    return UserRepository.find_by_username(username)


def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Return user data searched by id."""
    return UserRepository.find_by_id(user_id)


def save_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a new user record."""
    return UserRepository.create(user)


# --- Expenses ---
def get_all_expenses() -> List[Dict[str, Any]]:
    """Return every expense record."""
    return ExpenseRepository.list_all()


def find_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    """Return an expense by id."""
    return ExpenseRepository.find(expense_id)


def get_user_expenses(user_id: int) -> List[Dict[str, Any]]:
    """Return expenses for the provided user."""
    return ExpenseRepository.list_for_user(user_id)


def save_expense(expense: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new expense row."""
    return ExpenseRepository.create(expense)


def update_expense(expense_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing expense."""
    return ExpenseRepository.update(expense_id, updates)


def delete_expense(expense_id: int) -> bool:
    """Remove an expense row."""
    return ExpenseRepository.delete(expense_id)


def summary_by_category(user_id: int) -> Dict[str, float]:
    """Aggregate expenses by category."""
    return ExpenseRepository.summary_by_category(user_id)


def monthly_totals(user_id: int) -> Dict[str, float]:
    """Aggregate expenses by YYYY-MM month."""
    return ExpenseRepository.monthly_totals(user_id)


# --- Budgets ---
def get_budget(user_id: int, month: str) -> Optional[Dict[str, Any]]:
    """Return budget row for a given user and YYYY-MM month, or None."""
    return BudgetRepository.get_for_month(user_id, month)


def upsert_budget(user_id: int, month: str, limit_amount: float) -> Dict[str, Any]:
    """Create or update the budget for the given user and month."""
    return BudgetRepository.upsert(user_id, month, limit_amount)


def get_budget_status(user_id: int, month: str) -> Dict[str, Any]:
    """Return structured budget status for a month: limit, spent, remaining, status."""
    budget = get_budget(user_id, month)
    totals = monthly_totals(user_id)
    spent = float(totals.get(month, 0.0))
    if not budget:
        return {
            "month": month,
            "limit": None,
            "spent": spent,
            "remaining": None,
            "status": "no_budget",
        }
    limit_val = float(budget["limit_amount"]) if budget else 0.0
    remaining = max(limit_val - spent, 0.0)
    ratio = spent / limit_val if limit_val > 0 else 0.0
    if limit_val <= 0:
        status = "no_budget"
    elif spent > limit_val:
        status = "over"
    elif ratio >= 0.9:
        status = "warning"
    else:
        status = "ok"
    return {
        "month": month,
        "limit": limit_val,
        "spent": spent,
        "remaining": remaining,
        "status": status,
    }


# --- Categories ---
def _ensure_default_categories(user_id: int) -> None:
    """Seed defaults if the user has no categories."""
    CategoryRepository.ensure_defaults(user_id)


def list_categories(user_id: int) -> List[Dict[str, Any]]:
    """Return all categories for the given user."""
    _ensure_default_categories(user_id)
    return CategoryRepository.list_for_user(user_id)


def add_category(user_id: int, name: str) -> Dict[str, Any]:
    """Insert a category for the given user."""
    return CategoryRepository.add(user_id, name)


def delete_category(user_id: int, category_id: int) -> bool:
    """Delete a category owned by the user."""
    return CategoryRepository.delete(user_id, category_id)