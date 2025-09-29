"""
Migrate existing JSON data (users.json, expenses.json) into the database.

Usage:
  USE_DB=1 python migrate_json_to_db.py
"""
import json
import os
from datetime import datetime

from db import get_session, ENGINE
from models import Base, User, Expense


BASE_DIR = os.path.dirname(__file__)
USERS_JSON = os.path.join(BASE_DIR, "users.json")
EXP_JSON = os.path.join(BASE_DIR, "expenses.json")


def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or []
    except Exception:
        return []


def migrate_users():
    users = load_json(USERS_JSON)
    inserted = 0
    with get_session() as session:
        for u in users:
            username = u.get("username")
            pw_hash = u.get("password_hash")
            if not username or not pw_hash:
                continue
            exists = session.query(User).filter(User.username == username).first()
            if exists:
                continue
            obj = User(username=username, password_hash=pw_hash)
            session.add(obj)
            inserted += 1
    return inserted


def migrate_expenses():
    exps = load_json(EXP_JSON)
    inserted = 0
    with get_session() as session:
        for e in exps:
            try:
                user_id = int(e.get("user_id"))
                amount = float(e.get("amount"))
            except Exception:
                continue
            category = e.get("category") or "Uncategorized"
            note = e.get("note") or ""
            ds = e.get("date")
            d = None
            if ds:
                try:
                    d = datetime.fromisoformat(ds).date()
                except Exception:
                    d = None
            obj = Expense(user_id=user_id, amount=amount, category=category, date=d, note=note)
            session.add(obj)
            inserted += 1
    return inserted


def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=ENGINE)
    iu = migrate_users()
    ie = migrate_expenses()
    print(f"Migrated users: {iu}, expenses: {ie}")


if __name__ == "__main__":
    main()


