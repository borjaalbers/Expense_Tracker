"""
Integration tests exercising full workflows using a real in-memory database.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Tuple

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
        db_categories = session.execute(select(Category).where(Category.user_id == user["id"])).scalars().all()
        names = [cat.name for cat in db_categories]
        assert "Side Hustle" not in names
"""
Integration tests for full user workflows and end-to-end operations.

These tests verify complete workflows using real database operations,
not mocks, to ensure all components work together correctly.
"""
import pytest
import json
from datetime import date, datetime
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from contextlib import contextmanager

from models import User, Expense, Budget, Category
import storage_db


class TestFullUserWorkflow:
    """Test complete user workflows from signup to dashboard usage."""

    def test_signup_add_expense_view_dashboard_workflow(self, client, test_db_engine, test_db_session):
        """Test complete workflow: signup → add expense → view dashboard data."""
        # Setup: Patch db.get_session to use test database
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Step 1: Signup
                response = client.post('/api/signup',
                                      data=json.dumps({
                                          'username': 'newuser',
                                          'password': 'password123'
                                      }),
                                      content_type='application/json')
                
                assert response.status_code == 201
                signup_data = json.loads(response.data)
                assert signup_data['message'] == 'created'
                user_id = signup_data['user']['id']
                
                # Verify user was created in database
                test_db_session.commit()
                user = test_db_session.get(User, user_id)
                assert user is not None
                assert user.username == 'newuser'
                
                # Step 2: Add expense (user is now logged in from signup)
                response = client.post('/api/expenses',
                                      data=json.dumps({
                                          'amount': 50.0,
                                          'category': 'Food & Dining',
                                          'date': '2024-01-15',
                                          'note': 'Lunch'
                                      }),
                                      content_type='application/json')
                
                assert response.status_code == 201
                expense_data = json.loads(response.data)
                assert expense_data['amount'] == 50.0
                expense_id = expense_data['id']
                
                # Verify expense was saved in database
                test_db_session.commit()
                expense = test_db_session.get(Expense, expense_id)
                assert expense is not None
                assert expense.user_id == user_id
                assert expense.amount == 50.0
                
                # Step 3: View expenses list
                response = client.get('/api/expenses')
                assert response.status_code == 200
                expenses = json.loads(response.data)
                assert len(expenses) == 1
                assert expenses[0]['amount'] == 50.0
                
                # Step 4: Get summary (for dashboard charts)
                response = client.get('/api/summary')
                assert response.status_code == 200
                summary = json.loads(response.data)
                assert 'Food & Dining' in summary
                assert summary['Food & Dining'] == 50.0
                
                # Step 5: Get monthly totals
                response = client.get('/api/monthly')
                assert response.status_code == 200
                monthly = json.loads(response.data)
                assert '2024-01' in monthly
                assert monthly['2024-01'] == 50.0


class TestDatabaseOperationsEndToEnd:
    """Test database operations work end-to-end without mocks."""

    def test_user_crud_operations(self, test_db_engine, test_db_session):
        """Test complete user CRUD operations using real database."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Create user
                user_data = {
                    'username': 'testuser',
                    'password_hash': generate_password_hash('password123')
                }
                saved_user = storage_db.save_user(user_data)
                assert saved_user['id'] is not None
                assert saved_user['username'] == 'testuser'
                
                # Read user
                found_user = storage_db.find_user_by_username('testuser')
                assert found_user is not None
                assert found_user['id'] == saved_user['id']
                
                # Verify in database
                test_db_session.commit()
                db_user = test_db_session.get(User, saved_user['id'])
                assert db_user.username == 'testuser'

    def test_expense_crud_operations(self, test_db_engine, test_db_session, sample_user):
        """Test complete expense CRUD operations using real database."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Create expense
                expense_data = {
                    'user_id': sample_user.id,
                    'amount': 100.0,
                    'category': 'Shopping',
                    'date': '2024-02-10',
                    'note': 'Test purchase'
                }
                saved_expense = storage_db.save_expense(expense_data)
                assert saved_expense['id'] is not None
                assert saved_expense['amount'] == 100.0
                
                # Read expense
                found_expense = storage_db.find_expense(saved_expense['id'])
                assert found_expense is not None
                assert found_expense['amount'] == 100.0
                
                # Update expense
                updated = storage_db.update_expense(saved_expense['id'], {'amount': 150.0, 'note': 'Updated'})
                assert updated['amount'] == 150.0
                assert updated['note'] == 'Updated'
                
                # Verify in database
                test_db_session.commit()
                db_expense = test_db_session.get(Expense, saved_expense['id'])
                assert db_expense.amount == 150.0
                
                # Delete expense
                deleted = storage_db.delete_expense(saved_expense['id'])
                assert deleted is True
                
                # Commit and verify deleted
                test_db_session.commit()
                found_after_delete = storage_db.find_expense(saved_expense['id'])
                assert found_after_delete is None

    def test_budget_crud_operations(self, test_db_engine, test_db_session, sample_user):
        """Test complete budget CRUD operations using real database."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Create budget
                budget = storage_db.upsert_budget(sample_user.id, '2024-03', 1000.0)
                assert budget['id'] is not None
                assert budget['limit_amount'] == 1000.0
                assert budget['month'] == '2024-03'
                
                # Read budget
                found_budget = storage_db.get_budget(sample_user.id, '2024-03')
                assert found_budget is not None
                assert found_budget['limit_amount'] == 1000.0
                
                # Update budget (upsert)
                updated_budget = storage_db.upsert_budget(sample_user.id, '2024-03', 1500.0)
                assert updated_budget['limit_amount'] == 1500.0
                assert updated_budget['id'] == budget['id']  # Same budget, updated

    def test_category_crud_operations(self, test_db_engine, test_db_session, sample_user):
        """Test complete category CRUD operations using real database."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # List categories (should trigger default categories creation)
                # First call creates defaults, need to commit
                categories = storage_db.list_categories(sample_user.id)
                test_db_session.commit()  # Commit the default categories creation
                categories = storage_db.list_categories(sample_user.id)  # Get them again
                assert len(categories) > 0  # Default categories should be created
                
                # Add custom category
                new_category = storage_db.add_category(sample_user.id, 'Custom Category')
                assert new_category['id'] is not None
                assert new_category['name'] == 'Custom Category'
                
                # Verify in list
                updated_categories = storage_db.list_categories(sample_user.id)
                category_names = [c['name'] for c in updated_categories]
                assert 'Custom Category' in category_names
                
                # Delete category
                deleted = storage_db.delete_category(sample_user.id, new_category['id'])
                assert deleted is True
                
                # Commit and verify deleted
                test_db_session.commit()
                final_categories = storage_db.list_categories(sample_user.id)
                final_names = [c['name'] for c in final_categories]
                assert 'Custom Category' not in final_names


class TestAuthenticationFlow:
    """Test complete authentication flow end-to-end."""

    def test_signup_signin_signout_flow(self, client, test_db_engine, test_db_session):
        """Test complete authentication flow: signup → signin → signout."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Step 1: Signup
                response = client.post('/api/signup',
                                      data=json.dumps({
                                          'username': 'authuser',
                                          'password': 'authpass123'
                                      }),
                                      content_type='application/json')
                
                assert response.status_code == 201
                signup_data = json.loads(response.data)
                user_id = signup_data['user']['id']
                
                # Verify session is set
                with client.session_transaction() as sess:
                    assert sess.get('user_id') == user_id
                    assert sess.get('username') == 'authuser'
                
                # Step 2: Signout
                response = client.post('/api/signout')
                assert response.status_code == 200
                
                # Verify session is cleared
                with client.session_transaction() as sess:
                    assert sess.get('user_id') is None
                    assert sess.get('username') is None
                
                # Step 3: Signin
                response = client.post('/api/signin',
                                      data=json.dumps({
                                          'username': 'authuser',
                                          'password': 'authpass123'
                                      }),
                                      content_type='application/json')
                
                assert response.status_code == 200
                signin_data = json.loads(response.data)
                assert signin_data['message'] == 'signed in'
                
                # Verify session is set again
                with client.session_transaction() as sess:
                    assert sess.get('user_id') == user_id
                    assert sess.get('username') == 'authuser'
                
                # Step 4: Try to access protected endpoint
                response = client.get('/api/expenses')
                assert response.status_code == 200  # Should work when authenticated

    def test_authentication_protection(self, client, test_db_engine, test_db_session):
        """Test that protected endpoints require authentication."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Try to access protected endpoint without authentication
                response = client.get('/api/expenses')
                assert response.status_code == 401
                
                response = client.get('/api/summary')
                assert response.status_code == 401
                
                response = client.post('/api/expenses',
                                      data=json.dumps({'amount': 50.0, 'category': 'Food'}),
                                      content_type='application/json')
                assert response.status_code == 401


class TestBudgetCalculationLogic:
    """Test budget calculation logic with real data."""

    def test_budget_status_calculation(self, test_db_engine, test_db_session, sample_user):
        """Test budget status calculation with actual expenses."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Set budget
                budget = storage_db.upsert_budget(sample_user.id, '2024-03', 1000.0)
                
                # Add expenses for the month
                expense1 = storage_db.save_expense({
                    'user_id': sample_user.id,
                    'amount': 300.0,
                    'category': 'Food',
                    'date': '2024-03-15',
                    'note': 'Groceries'
                })
                
                expense2 = storage_db.save_expense({
                    'user_id': sample_user.id,
                    'amount': 200.0,
                    'category': 'Transport',
                    'date': '2024-03-20',
                    'note': 'Gas'
                })
                
                # Get budget status
                status = storage_db.get_budget_status(sample_user.id, '2024-03')
                
                assert status['month'] == '2024-03'
                assert status['limit'] == 1000.0
                assert status['spent'] == 500.0  # 300 + 200
                assert status['remaining'] == 500.0
                assert status['status'] == 'ok'

    def test_budget_warning_threshold(self, test_db_engine, test_db_session, sample_user):
        """Test budget warning status when approaching limit."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Set budget
                storage_db.upsert_budget(sample_user.id, '2024-04', 1000.0)
                
                # Add expenses to reach 90% (warning threshold)
                storage_db.save_expense({
                    'user_id': sample_user.id,
                    'amount': 920.0,
                    'category': 'Shopping',
                    'date': '2024-04-15',
                    'note': 'Large purchase'
                })
                
                status = storage_db.get_budget_status(sample_user.id, '2024-04')
                assert status['status'] == 'warning'
                assert status['spent'] == 920.0
                assert status['remaining'] == 80.0

    def test_budget_over_limit(self, test_db_engine, test_db_session, sample_user):
        """Test budget status when over limit."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Set budget
                storage_db.upsert_budget(sample_user.id, '2024-05', 1000.0)
                
                # Add expenses over limit
                storage_db.save_expense({
                    'user_id': sample_user.id,
                    'amount': 1100.0,
                    'category': 'Shopping',
                    'date': '2024-05-15',
                    'note': 'Overspent'
                })
                
                status = storage_db.get_budget_status(sample_user.id, '2024-05')
                assert status['status'] == 'over'
                assert status['spent'] == 1100.0
                assert status['remaining'] == 0.0

    def test_budget_no_budget_set(self, test_db_engine, test_db_session, sample_user):
        """Test budget status when no budget is set."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Add expenses without setting budget
                storage_db.save_expense({
                    'user_id': sample_user.id,
                    'amount': 500.0,
                    'category': 'Food',
                    'date': '2024-06-15',
                    'note': 'Expenses'
                })
                
                status = storage_db.get_budget_status(sample_user.id, '2024-06')
                assert status['status'] == 'no_budget'
                assert status['limit'] is None
                assert status['spent'] == 500.0
                assert status['remaining'] is None


class TestCategoryManagementFlow:
    """Test complete category management workflow."""

    def test_category_workflow(self, client, test_db_engine, test_db_session, sample_user):
        """Test complete category management: list → add → use → delete."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Login user
                with client.session_transaction() as sess:
                    sess['user_id'] = sample_user.id
                    sess['username'] = sample_user.username
                
                # Step 1: List categories (should include defaults)
                # First call creates defaults
                response = client.get('/api/categories')
                test_db_session.commit()  # Commit default categories
                # Get again to verify
                response = client.get('/api/categories')
                assert response.status_code == 200
                categories = json.loads(response.data)
                assert len(categories) > 0
                initial_count = len(categories)
                
                # Step 2: Add new category
                response = client.post('/api/categories',
                                      data=json.dumps({'name': 'My Custom Category'}),
                                      content_type='application/json')
                assert response.status_code == 201
                new_category = json.loads(response.data)
                category_id = new_category['id']
                
                # Step 3: Verify category is in list
                response = client.get('/api/categories')
                categories = json.loads(response.data)
                assert len(categories) == initial_count + 1
                category_names = [c['name'] for c in categories]
                assert 'My Custom Category' in category_names
                
                # Step 4: Use category in expense
                response = client.post('/api/expenses',
                                      data=json.dumps({
                                          'amount': 75.0,
                                          'category': 'My Custom Category',
                                          'date': '2024-01-20',
                                          'note': 'Test'
                                      }),
                                      content_type='application/json')
                assert response.status_code == 201
                expense = json.loads(response.data)
                assert expense['category'] == 'My Custom Category'
                
                # Step 5: Delete category
                response = client.delete(f'/api/categories/{category_id}')
                assert response.status_code == 200
                
                # Commit deletion
                test_db_session.commit()
                
                # Step 6: Verify category is removed
                response = client.get('/api/categories')
                categories = json.loads(response.data)
                category_names = [c['name'] for c in categories]
                assert 'My Custom Category' not in category_names

    def test_default_categories_creation(self, test_db_engine, test_db_session, sample_user):
        """Test that default categories are created on first access."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # First access should create default categories
                categories = storage_db.list_categories(sample_user.id)
                test_db_session.commit()  # Commit the default categories
                categories = storage_db.list_categories(sample_user.id)  # Get them again
                assert len(categories) >= 10  # Should have default categories
                
                # Verify some default categories exist
                category_names = [c['name'] for c in categories]
                assert 'Food & Dining' in category_names
                assert 'Transportation' in category_names
                assert 'Shopping' in category_names

    def test_category_idempotency(self, test_db_engine, test_db_session, sample_user):
        """Test that adding the same category twice returns existing."""
        @contextmanager
        def mock_get_session():
            yield test_db_session
        
        with patch('db.get_session', mock_get_session):
            with patch('storage_db.get_session', mock_get_session):
                # Add category first time
                cat1 = storage_db.add_category(sample_user.id, 'Duplicate Test')
                cat1_id = cat1['id']
                
                # Add same category again
                cat2 = storage_db.add_category(sample_user.id, 'Duplicate Test')
                
                # Should return the same category
                assert cat2['id'] == cat1_id
                assert cat2['name'] == 'Duplicate Test'
