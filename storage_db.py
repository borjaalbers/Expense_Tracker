from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import NoResultFound

from db import get_session
from models import User, Expense


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


def get_user_expenses(user_id: int) -> List[Dict[str, Any]]:
    with get_session() as session:
        exps = session.scalars(
            select(Expense).where(Expense.user_id == user_id)
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
        date_value: Optional[date]
        ds = expense.get("date")
        if ds:
            date_value = datetime.fromisoformat(ds).date()
        else:
            date_value = None
        obj = Expense(
            user_id=expense["user_id"],
            amount=float(expense["amount"]),
            category=expense.get("category", "Uncategorized"),
            date=date_value,
            note=expense.get("note", ""),
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


def find_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        e = session.get(Expense, expense_id)
        if not e:
            return None
        return {
            "id": e.id,
            "user_id": e.user_id,
            "amount": float(e.amount),
            "category": e.category,
            "date": e.date.isoformat() if e.date else None,
            "note": e.note,
        }


def update_expense(expense_id: int, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with get_session() as session:
        e = session.get(Expense, expense_id)
        if not e:
            return None
        if "amount" in update_fields:
            e.amount = float(update_fields["amount"])
        if "category" in update_fields:
            e.category = str(update_fields["category"]) or "Uncategorized"
        if "date" in update_fields:
            ds = update_fields["date"]
            e.date = datetime.fromisoformat(ds).date() if ds else None
        if "note" in update_fields:
            e.note = str(update_fields["note"]) or ""
        session.flush()
        return {
            "id": e.id,
            "user_id": e.user_id,
            "amount": float(e.amount),
            "category": e.category,
            "date": e.date.isoformat() if e.date else None,
            "note": e.note,
        }


def delete_expense(expense_id: int) -> bool:
    with get_session() as session:
        e = session.get(Expense, expense_id)
        if not e:
            return False
        session.delete(e)
        return True


def summary_by_category(user_id: int) -> Dict[str, float]:
    with get_session() as session:
        rows = session.execute(
            select(Expense.category, func.sum(Expense.amount)).where(Expense.user_id == user_id).group_by(Expense.category)
        ).all()
        return {cat or "Uncategorized": float(total or 0.0) for cat, total in rows}


def monthly_totals(user_id: int) -> Dict[str, float]:
    with get_session() as session:
        # SQLite: use strftime to aggregate by YYYY-MM
        rows = session.execute(
            select(func.strftime('%Y-%m', Expense.date), func.sum(Expense.amount))
            .where(Expense.user_id == user_id)
            .group_by(func.strftime('%Y-%m', Expense.date))
        ).all()
        return {ym or "": float(total or 0.0) for ym, total in rows}


