# storage.py
import json
import os
from threading import Lock
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
EXP_FILE = os.path.join(BASE_DIR, "expenses.json")
_lock = Lock()

def _ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def _read(path: str):
    _ensure_file(path, [])
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _write(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Users ---
def get_all_users() -> List[Dict[str, Any]]:
    with _lock:
        return _read(USERS_FILE)

def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with _lock:
        users = _read(USERS_FILE)
        for u in users:
            if u.get("username") == username:
                return u
    return None

def find_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _lock:
        users = _read(USERS_FILE)
        for u in users:
            if u.get("id") == user_id:
                return u
    return None

def save_user(user: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        users = _read(USERS_FILE)
        max_id = max((u.get("id", 0) for u in users), default=0)
        user["id"] = max_id + 1
        users.append(user)
        _write(USERS_FILE, users)
        return user

# --- Expenses ---
def get_all_expenses() -> List[Dict[str, Any]]:
    with _lock:
        return _read(EXP_FILE)

def get_user_expenses(user_id: int) -> List[Dict[str, Any]]:
    with _lock:
        items = _read(EXP_FILE)
        return [it for it in items if it.get("user_id") == user_id]

def save_expense(expense: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        items = _read(EXP_FILE)
        max_id = max((it.get("id", 0) for it in items), default=0)
        expense["id"] = max_id + 1
        items.append(expense)
        _write(EXP_FILE, items)
        return expense

def find_expense(expense_id: int) -> Optional[Dict[str, Any]]:
    with _lock:
        items = _read(EXP_FILE)
        for it in items:
            if it.get("id") == expense_id:
                return it
    return None

def update_expense(expense_id: int, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with _lock:
        items = _read(EXP_FILE)
        for i, it in enumerate(items):
            if it.get("id") == expense_id:
                it.update(update_fields)
                items[i] = it
                _write(EXP_FILE, items)
                return it
    return None

def delete_expense(expense_id: int) -> bool:
    with _lock:
        items = _read(EXP_FILE)
        new_items = [it for it in items if it.get("id") != expense_id]
        if len(new_items) == len(items):
            return False
        _write(EXP_FILE, new_items)
        return True

def summary_by_category(user_id: int) -> Dict[str, float]:
    with _lock:
        items = _read(EXP_FILE)
        sums = {}
        for it in items:
            if it.get("user_id") != user_id:
                continue
            cat = it.get("category", "Uncategorized")
            try:
                amt = float(it.get("amount", 0))
            except (ValueError, TypeError):
                amt = 0.0
            sums[cat] = sums.get(cat, 0.0) + amt
        return sums

def monthly_totals(user_id: int) -> Dict[str, float]:
    """
    Returns monthly totals as {"YYYY-MM": total}
    """
    with _lock:
        items = _read(EXP_FILE)
        months = {}
        for it in items:
            if it.get("user_id") != user_id:
                continue
            date = it.get("date")
            if not date:
                continue
            # assume date is YYYY-MM-DD
            month = date[:7]
            try:
                amt = float(it.get("amount", 0))
            except (ValueError, TypeError):
                amt = 0.0
            months[month] = months.get(month, 0.0) + amt
        return months
