"""
Unit tests for Flask application routes.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestAuthRoutes:
    """Test authentication endpoints."""

    @patch('app.storage')
    def test_signup_success(self, mock_storage, client):
        """Test successful user signup."""
        mock_storage.find_user_by_username.return_value = None
        mock_storage.save_user.return_value = {'id': 1, 'username': 'newuser'}
        
        response = client.post('/api/signup', 
                              data=json.dumps({'username': 'newuser', 'password': 'pass123'}),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'created'
        assert data['user']['username'] == 'newuser'

    @patch('app.storage')
    def test_signup_duplicate_username(self, mock_storage, client):
        """Test signup with existing username."""
        mock_storage.find_user_by_username.return_value = {'id': 1, 'username': 'existing'}
        
        response = client.post('/api/signup',
                              data=json.dumps({'username': 'existing', 'password': 'pass123'}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        response = client.post('/api/signup',
                              data=json.dumps({'username': ''}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.storage')
    @patch('app.check_password_hash')
    def test_signin_success(self, mock_check_pw, mock_storage, client):
        """Test successful signin."""
        mock_storage.find_user_by_username.return_value = {
            'id': 1,
            'username': 'testuser',
            'password_hash': 'hashed'
        }
        mock_check_pw.return_value = True
        
        response = client.post('/api/signin',
                              data=json.dumps({'username': 'testuser', 'password': 'pass123'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'signed in'

    @patch('app.storage')
    def test_signin_invalid_username(self, mock_storage, client):
        """Test signin with non-existent username."""
        mock_storage.find_user_by_username.return_value = None
        
        response = client.post('/api/signin',
                              data=json.dumps({'username': 'nonexistent', 'password': 'pass'}),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid credentials' in data['error']

    @patch('app.storage')
    @patch('app.check_password_hash')
    def test_signin_invalid_password(self, mock_check_pw, mock_storage, client):
        """Test signin with wrong password."""
        mock_storage.find_user_by_username.return_value = {
            'id': 1,
            'username': 'testuser',
            'password_hash': 'hashed'
        }
        mock_check_pw.return_value = False
        
        response = client.post('/api/signin',
                              data=json.dumps({'username': 'testuser', 'password': 'wrong'}),
                              content_type='application/json')
        
        assert response.status_code == 401

    def test_signout(self, client):
        """Test signout endpoint."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
        
        response = client.post('/api/signout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'signed out'


class TestExpenseRoutes:
    """Test expense CRUD endpoints."""

    @patch('app.storage')
    @patch('app.current_user')
    def test_add_expense_success(self, mock_current_user, mock_storage, client):
        """Test adding a valid expense."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.save_expense.return_value = {
            'id': 10,
            'user_id': 1,
            'amount': 50.0,
            'category': 'Food',
            'date': '2024-01-15',
            'note': 'Lunch'
        }
        
        response = client.post('/api/expenses',
                              data=json.dumps({
                                  'amount': 50.0,
                                  'category': 'Food',
                                  'date': '2024-01-15',
                                  'note': 'Lunch'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['amount'] == 50.0

    @patch('app.current_user')
    def test_add_expense_unauthenticated(self, mock_current_user, client):
        """Test adding expense without authentication."""
        mock_current_user.return_value = None
        
        response = client.post('/api/expenses',
                              data=json.dumps({'amount': 50.0, 'category': 'Food'}),
                              content_type='application/json')
        
        assert response.status_code == 401

    @patch('app.current_user')
    def test_add_expense_invalid_amount(self, mock_current_user, client):
        """Test adding expense with invalid amount."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/expenses',
                              data=json.dumps({'amount': -10.0, 'category': 'Food'}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'greater than 0' in data['error']

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_expenses(self, mock_current_user, mock_storage, client):
        """Test listing user expenses."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_user_expenses.return_value = [
            {'id': 1, 'amount': 10.0, 'category': 'Food', 'date': '2024-01-01', 'note': ''},
            {'id': 2, 'amount': 20.0, 'category': 'Transport', 'date': '2024-01-02', 'note': ''}
        ]
        
        response = client.get('/api/expenses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_expense(self, mock_current_user, mock_storage, client):
        """Test getting a specific expense."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        
        response = client.get('/api/expenses/5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 5

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_expense_wrong_user(self, mock_current_user, mock_storage, client):
        """Test getting expense owned by another user."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 2,  # Different user
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        
        response = client.get('/api/expenses/5')
        
        assert response.status_code == 404

    @patch('app.storage')
    @patch('app.current_user')
    def test_update_expense(self, mock_current_user, mock_storage, client):
        """Test updating an expense."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Old'
        }
        mock_storage.update_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 150.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Updated'
        }
        
        response = client.put('/api/expenses/5',
                             data=json.dumps({'amount': 150.0, 'note': 'Updated'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['amount'] == 150.0

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_expense(self, mock_current_user, mock_storage, client):
        """Test deleting an expense."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        mock_storage.delete_expense.return_value = True
        
        response = client.delete('/api/expenses/5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['deleted'] == 5


class TestAnalyticsRoutes:
    """Test analytics endpoints."""

    @patch('app.storage')
    @patch('app.current_user')
    def test_summary(self, mock_current_user, mock_storage, client):
        """Test category summary endpoint."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.summary_by_category.return_value = {
            'Food': 100.0,
            'Transport': 50.0
        }
        
        response = client.get('/api/summary')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Food' in data
        assert data['Food'] == 100.0

    @patch('app.storage')
    @patch('app.current_user')
    def test_monthly(self, mock_current_user, mock_storage, client):
        """Test monthly totals endpoint."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.monthly_totals.return_value = {
            '2024-01': 200.0,
            '2024-02': 150.0
        }
        
        response = client.get('/api/monthly')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '2024-01' in data


class TestBudgetRoutes:
    """Test budget endpoints."""

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_budget(self, mock_current_user, mock_storage, client):
        """Test getting budget status."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_budget_status.return_value = {
            'month': '2024-03',
            'limit': 1000.0,
            'spent': 300.0,
            'remaining': 700.0,
            'status': 'ok'
        }
        
        response = client.get('/api/budget?month=2024-03')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['limit'] == 1000.0

    @patch('app.storage')
    @patch('app.current_user')
    def test_set_budget(self, mock_current_user, mock_storage, client):
        """Test setting a budget."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.upsert_budget.return_value = {
            'id': 1,
            'user_id': 1,
            'month': '2024-03',
            'limit_amount': 1000.0
        }
        mock_storage.get_budget_status.return_value = {
            'month': '2024-03',
            'limit': 1000.0,
            'spent': 0.0,
            'remaining': 1000.0,
            'status': 'ok'
        }
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03', 'limit_amount': 1000.0}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'budget' in data
        assert 'status' in data

    @patch('app.current_user')
    def test_set_budget_invalid_amount(self, mock_current_user, client):
        """Test setting budget with invalid amount."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03', 'limit_amount': -500}),
                              content_type='application/json')
        
        assert response.status_code == 400


class TestCategoryRoutes:
    """Test category endpoints."""

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_categories(self, mock_current_user, mock_storage, client):
        """Test listing categories."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.list_categories.return_value = [
            {'id': 1, 'name': 'Food'},
            {'id': 2, 'name': 'Transport'}
        ]
        
        response = client.get('/api/categories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

    @patch('app.storage')
    @patch('app.current_user')
    def test_add_category(self, mock_current_user, mock_storage, client):
        """Test adding a category."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.add_category.return_value = {'id': 5, 'name': 'Custom'}
        
        response = client.post('/api/categories',
                              data=json.dumps({'name': 'Custom'}),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Custom'

    @patch('app.current_user')
    def test_add_category_empty_name(self, mock_current_user, client):
        """Test adding category with empty name."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/categories',
                              data=json.dumps({'name': ''}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_category(self, mock_current_user, mock_storage, client):
        """Test deleting a category."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.delete_category.return_value = True
        
        response = client.delete('/api/categories/5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['deleted'] == 5

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_category_not_found(self, mock_current_user, mock_storage, client):
        """Test deleting non-existent category."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.delete_category.return_value = False
        
        response = client.delete('/api/categories/999')
        
        assert response.status_code == 404


class TestHealthRoute:
    """Test health check endpoint."""

    def test_health(self, client):
        """Test health endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestPageRoutes:
    """Test HTML page routes."""

    def test_index_not_logged_in(self, client):
        """Test index page when not logged in."""
        response = client.get('/')
        
        assert response.status_code == 200

    @patch('app.current_user')
    def test_index_logged_in_redirect(self, mock_current_user, client):
        """Test index redirects to dashboard when logged in."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.get('/')
        
        assert response.status_code == 302
        assert '/dashboard' in response.location

    @patch('app.current_user')
    def test_dashboard_logged_in(self, mock_current_user, client):
        """Test dashboard access when logged in."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.get('/dashboard')
        
        assert response.status_code == 200

    @patch('app.current_user')
    def test_dashboard_not_logged_in_redirect(self, mock_current_user, client):
        """Test dashboard redirects to index when not logged in."""
        mock_current_user.return_value = None
        
        response = client.get('/dashboard')
        
        assert response.status_code == 302
        assert '/' in response.location


class TestExpenseEdgeCases:
    """Test edge cases and error paths for expenses."""

    @patch('app.current_user')
    def test_add_expense_missing_amount(self, mock_current_user, client):
        """Test adding expense with missing amount."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/expenses',
                              data=json.dumps({'category': 'Food'}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.current_user')
    def test_add_expense_invalid_date_format(self, mock_current_user, client):
        """Test adding expense with invalid date."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/expenses',
                              data=json.dumps({
                                  'amount': 50.0,
                                  'category': 'Food',
                                  'date': 'invalid-date'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'date' in data['error'].lower()

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_expenses_with_category_filter(self, mock_current_user, mock_storage, client):
        """Test listing expenses filtered by category."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_user_expenses.return_value = [
            {'id': 1, 'amount': 10.0, 'category': 'Food', 'date': '2024-01-01', 'note': ''},
            {'id': 2, 'amount': 20.0, 'category': 'Transport', 'date': '2024-01-02', 'note': ''}
        ]
        
        response = client.get('/api/expenses?category=Food')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(exp['category'] == 'Food' for exp in data)

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_expenses_with_date_range(self, mock_current_user, mock_storage, client):
        """Test listing expenses with date range filter."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_user_expenses.return_value = [
            {'id': 1, 'amount': 10.0, 'category': 'Food', 'date': '2024-01-15', 'note': ''},
            {'id': 2, 'amount': 20.0, 'category': 'Transport', 'date': '2024-02-01', 'note': ''}
        ]
        
        response = client.get('/api/expenses?date_from=2024-01-01&date_to=2024-01-31')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_expense_not_found(self, mock_current_user, mock_storage, client):
        """Test getting non-existent expense."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = None
        
        response = client.get('/api/expenses/999')
        
        assert response.status_code == 404

    @patch('app.current_user')
    def test_update_expense_invalid_date(self, mock_current_user, client):
        """Test updating expense with invalid date format."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        with patch('app.storage') as mock_storage:
            mock_storage.find_expense.return_value = {
                'id': 5,
                'user_id': 1,
                'amount': 100.0,
                'category': 'Shopping',
                'date': '2024-01-10',
                'note': 'Test'
            }
            
            response = client.put('/api/expenses/5',
                                 data=json.dumps({'date': 'bad-date'}),
                                 content_type='application/json')
            
            assert response.status_code == 400

    @patch('app.storage')
    @patch('app.current_user')
    def test_update_expense_no_fields(self, mock_current_user, mock_storage, client):
        """Test updating expense with no valid fields."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        
        response = client.put('/api/expenses/5',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'no valid' in data['error'].lower()

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_expense_failed(self, mock_current_user, mock_storage, client):
        """Test delete expense when storage fails."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 1,
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        mock_storage.delete_expense.return_value = False
        
        response = client.delete('/api/expenses/5')
        
        assert response.status_code == 500


class TestBudgetEdgeCases:
    """Test edge cases for budget endpoints."""

    @patch('app.current_user')
    def test_get_budget_unauthenticated(self, mock_current_user, client):
        """Test getting budget without authentication."""
        mock_current_user.return_value = None
        
        response = client.get('/api/budget')
        
        assert response.status_code == 401

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_budget_default_month(self, mock_current_user, mock_storage, client):
        """Test getting budget without specifying month (uses current)."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_budget_status.return_value = {
            'month': datetime.utcnow().strftime("%Y-%m"),
            'limit': 1000.0,
            'spent': 0.0,
            'remaining': 1000.0,
            'status': 'ok'
        }
        
        response = client.get('/api/budget')
        
        assert response.status_code == 200

    @patch('app.current_user')
    def test_get_budget_invalid_month_format(self, mock_current_user, client):
        """Test getting budget with invalid month format."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.get('/api/budget?month=invalid')
        
        assert response.status_code == 400

    @patch('app.current_user')
    def test_set_budget_unauthenticated(self, mock_current_user, client):
        """Test setting budget without authentication."""
        mock_current_user.return_value = None
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03', 'limit_amount': 1000}),
                              content_type='application/json')
        
        assert response.status_code == 401

    @patch('app.current_user')
    def test_set_budget_invalid_month_format(self, mock_current_user, client):
        """Test setting budget with invalid month format."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': 'bad-month', 'limit_amount': 1000}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.current_user')
    def test_set_budget_missing_amount(self, mock_current_user, client):
        """Test setting budget with missing limit_amount."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03'}),
                              content_type='application/json')
        
        assert response.status_code == 400


class TestCategoryEdgeCases:
    """Test edge cases for category endpoints."""

    @patch('app.current_user')
    def test_list_categories_unauthenticated(self, mock_current_user, client):
        """Test listing categories without authentication."""
        mock_current_user.return_value = None
        
        response = client.get('/api/categories')
        
        assert response.status_code == 401

    @patch('app.current_user')
    def test_add_category_unauthenticated(self, mock_current_user, client):
        """Test adding category without authentication."""
        mock_current_user.return_value = None
        
        response = client.post('/api/categories',
                              data=json.dumps({'name': 'Test'}),
                              content_type='application/json')
        
        assert response.status_code == 401

    @patch('app.storage')
    @patch('app.current_user')
    def test_add_category_value_error(self, mock_current_user, mock_storage, client):
        """Test adding category when storage raises ValueError."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.add_category.side_effect = ValueError('Invalid name')
        
        response = client.post('/api/categories',
                              data=json.dumps({'name': 'Test'}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.current_user')
    def test_delete_category_unauthenticated(self, mock_current_user, client):
        """Test deleting category without authentication."""
        mock_current_user.return_value = None
        
        response = client.delete('/api/categories/1')
        
        assert response.status_code == 401

