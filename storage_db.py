from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import NoResultFound

from db import get_session
from models import User, Expense, Budget


# --- Users ---
def get_all_users() -> List[Dict[str, Any]]:
    with get_session() as session:
        users = session.scalars(select(User).order_by(User.id.asc())).all()
        return [
            {"id": u.id, "username": u.username, "password_hash": u.password_hash}
            for u in users
        ]


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if not user:
            return None
        return {"id": user.id, "username": user.username, "password_hash": user.password_hash}


def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return None
        return {"id": user.id, "username": user.username, "password_hash": user.password_hash}


def save_user(user: Dict[str, Any]) -> Dict[str, Any]:
    with get_session() as session:
        obj = User(username=user["username"], password_hash=user["password_hash"])
        session.add(obj)
        session.flush()
        return {"id": obj.id, "username": obj.username, "password_hash": obj.password_hash}


# --- Expenses ---
def get_all_expenses() -> List[Dict[str, Any]]:
    with get_session() as session:
        exps = session.scalars(select(Expense).order_by(Expense.id.asc())).all()
        return [
            {
                "id": e.id,
                "user_id": e.user_id,
                "amount": float(e.amount),
                "category": e.category,
                "date": e.date.isoformat() if e.date else None,
                "note": e.note,
            }
            for e in exps
        ]


def find_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        exp = session.get(Expense, expense_id)
        if not exp:
            return None
        return {
            "id": exp.id,
            "user_id": exp.user_id,
            "amount": float(exp.amount),
            "category": exp.category,
            "date": exp.date.isoformat() if exp.date else None,
            "note": exp.note,
        }


def get_user_expenses(user_id: int) -> List[Dict[str, Any]]:
    with get_session() as session:
        exps = session.scalars(
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.date.desc(), Expense.id.desc())
        ).all()
        return [
            {
                "id": e.id,
                "user_id": e.user_id,
                "amount": float(e.amount),
                "category": e.category,
                "date": e.date.isoformat() if e.date else None,
                "note": e.note,
            }
            for e in exps
        ]


def save_expense(expense: Dict[str, Any]) -> Dict[str, Any]:
    with get_session() as session:
        date_obj = None
        if expense.get("date"):
            date_obj = date.fromisoformat(expense["date"])
        obj = Expense(
            user_id=expense["user_id"],
            amount=expense["amount"],
            category=expense["category"],
            date=date_obj,
            note=expense["note"],
        )
        session.add(obj)
        session.flush()
        return {
            "id": obj.id,
            "user_id": obj.user_id,
            "amount": float(obj.amount),
            "category": obj.category,
            "date": obj.date.isoformat() if obj.date else None,
            "note": obj.note,
        }


def update_expense(expense_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        exp = session.get(Expense, expense_id)
        if not exp:
            return None
        for key, value in updates.items():
            if key == "date" and value:
                setattr(exp, key, date.fromisoformat(value))
            else:
                setattr(exp, key, value)
        session.flush()
        return {
            "id": exp.id,
            "user_id": exp.user_id,
            "amount": float(exp.amount),
            "category": exp.category,
            "date": exp.date.isoformat() if exp.date else None,
            "note": exp.note,
        }


def delete_expense(expense_id: int) -> bool:
    with get_session() as session:
        exp = session.get(Expense, expense_id)
        if not exp:
            return False
        session.delete(exp)
        return True


def summary_by_category(user_id: int) -> Dict[str, float]:
    with get_session() as session:
        rows = session.execute(
            select(Expense.category, func.sum(Expense.amount))
            .where(Expense.user_id == user_id)
            .group_by(Expense.category)
        ).all()
        return {cat or "Uncategorized": float(total or 0.0) for cat, total in rows}


def monthly_totals(user_id: int) -> Dict[str, float]:
    with get_session() as session:
        rows = session.execute(
            select(func.strftime('%Y-%m', Expense.date), func.sum(Expense.amount))
            .where(Expense.user_id == user_id)
            .group_by(func.strftime('%Y-%m', Expense.date))
        ).all()
        return {ym or "": float(total or 0.0) for ym, total in rows}


# --- Budgets ---
def get_budget(user_id: int, month: str) -> Optional[Dict[str, Any]]:
    """Return budget row for a given user and YYYY-MM month, or None."""
    with get_session() as session:
        obj = session.execute(
            select(Budget).where(Budget.user_id == user_id, Budget.month == month)
        ).scalar_one_or_none()
        if not obj:
            return None
        return {
            "id": obj.id,
            "user_id": obj.user_id,
            "month": obj.month,
            "limit_amount": float(obj.limit_amount),
        }


def upsert_budget(user_id: int, month: str, limit_amount: float) -> Dict[str, Any]:
    """Create or update the budget for the given user and month."""
    with get_session() as session:
        obj = session.execute(
            select(Budget).where(Budget.user_id == user_id, Budget.month == month)
        ).scalar_one_or_none()
        if obj:
            obj.limit_amount = limit_amount
        else:
            obj = Budget(user_id=user_id, month=month, limit_amount=limit_amount)
            session.add(obj)
        session.flush()
        return {
            "id": obj.id,
            "user_id": obj.user_id,
            "month": obj.month,
            "limit_amount": float(obj.limit_amount),
        }


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