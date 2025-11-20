"""
Integration tests exercising full workflows using a real in-memory database.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Dict

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app as flask_app
import storage_db
from models import Base, User, Expense, Budget, Category


@pytest.fixture(name="integration_app")
def fixture_integration_app(monkeypatch):
    """Provide a Flask client backed by an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    @contextmanager
    def get_session():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Patch storage_db to use the in-memory session factory
    monkeypatch.setattr(storage_db, "get_session", get_session)
    monkeypatch.setattr(flask_app, "storage", storage_db)

    with flask_app.app.test_client() as client:
        yield client, SessionLocal


def _signup(client) -> Dict[str, int]:
    response = client.post(
        "/api/signup",
        json={"username": "integration", "password": "secret123"},
    )
    assert response.status_code == 201
    return response.get_json()["user"]


def _signin(client):
    response = client.post(
        "/api/signin",
        json={"username": "integration", "password": "secret123"},
    )
    assert response.status_code == 200


def _signout(client):
    response = client.post("/api/signout")
    assert response.status_code == 200


def test_full_user_workflow(integration_app):
    """User can sign up, add an expense, and see it reflected in summary endpoints."""
    client, SessionLocal = integration_app
    user = _signup(client)

    expense_payload = {
        "amount": 42.5,
        "category": "Groceries",
        "date": "2024-03-10",
        "note": "Weekly shopping",
    }
    response = client.post("/api/expenses", json=expense_payload)
    assert response.status_code == 201
    saved = response.get_json()
    assert saved["amount"] == 42.5

    # Verify expense persisted in database
    with SessionLocal() as session:
        db_expense = session.execute(select(Expense)).scalar_one()
        assert db_expense.user_id == user["id"]
        assert float(db_expense.amount) == 42.5

    # Summary endpoints should reflect the expense
    summary = client.get("/api/summary").get_json()
    assert summary["Groceries"] == 42.5

    monthly = client.get("/api/monthly").get_json()
    assert monthly["2024-03"] == 42.5


def test_authentication_flow(integration_app):
    """Complete authentication flow including sign out and protected access."""
    client, _ = integration_app

    _signup(client)
    _signout(client)

    # Protected endpoint after signout should fail
    response = client.get("/api/expenses")
    assert response.status_code == 401

    _signin(client)
    response = client.get("/api/expenses")
    assert response.status_code == 200


def test_database_operations_end_to_end(integration_app):
    """Budget endpoints perform create/read operations backed by the real database."""
    client, SessionLocal = integration_app
    user = _signup(client)

    response = client.post(
        "/api/budget",
        json={"month": "2024-04", "limit_amount": 1000.0},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["budget"]["limit_amount"] == 1000.0

    # Verify budget stored in database
    with SessionLocal() as session:
        db_budget = session.execute(select(Budget)).scalar_one()
        assert db_budget.user_id == user["id"]
        assert float(db_budget.limit_amount) == 1000.0


def test_budget_calculation_logic(integration_app):
    """Budget status reflects spending thresholds (ok/warning/over)."""
    client, _ = integration_app
    _signup(client)

    client.post("/api/budget", json={"month": "2024-05", "limit_amount": 100.0})
    client.post("/api/expenses", json={"amount": 95, "category": "Food", "date": "2024-05-10"})
    status = client.get("/api/budget?month=2024-05").get_json()
    assert status["status"] == "warning"

    client.post("/api/expenses", json={"amount": 20, "category": "Food", "date": "2024-05-12"})
    status = client.get("/api/budget?month=2024-05").get_json()
    assert status["status"] == "over"


def test_category_management_flow(integration_app):
    """User can list default categories, add a custom one, and then delete it."""
    client, SessionLocal = integration_app
    user = _signup(client)

    categories = client.get("/api/categories").get_json()
    assert "Food & Dining" in [cat["name"] for cat in categories]

    response = client.post("/api/categories", json={"name": "Side Hustle"})
    assert response.status_code == 201
    custom_id = response.get_json()["id"]

    client.post(
        "/api/expenses",
        json={"amount": 60, "category": "Side Hustle", "date": "2024-02-02"},
    )
    expenses = client.get("/api/expenses?category=Side Hustle").get_json()
    assert len(expenses) == 1

    delete_resp = client.delete(f"/api/categories/{custom_id}")
    assert delete_resp.status_code == 200

    # Verify category removed from database
    with SessionLocal() as session:
        db_categories = session.execute(
            select(Category).where(Category.user_id == user["id"])
        ).scalars().all()
        names = [cat.name for cat in db_categories]
        assert "Side Hustle" not in names
