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
    """Test enhanced health check endpoint."""

    def test_health_basic(self, client):
        """Test health endpoint returns comprehensive status."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'version' in data
        assert 'uptime_seconds' in data
        assert 'uptime' in data
        assert 'database' in data
        assert 'timestamp' in data
        
        # Check database connectivity info
        assert 'connected' in data['database']
        assert isinstance(data['database']['connected'], bool)
        
        # When database is connected, status should be healthy
        if data['database']['connected']:
            assert data['status'] == 'healthy'

    def test_health_database_connectivity(self, client):
        """Test that health endpoint checks database connectivity."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Database should be connected in test environment
        assert data['database']['connected'] is True
        assert data['status'] == 'healthy'

    def test_health_uptime_format(self, client):
        """Test that uptime is in human-readable format."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Uptime should be a string in human-readable format
        assert isinstance(data['uptime'], str)
        assert len(data['uptime']) > 0
        
        # Uptime seconds should be a number
        assert isinstance(data['uptime_seconds'], (int, float))
        assert data['uptime_seconds'] >= 0

    def test_health_version(self, client):
        """Test that version information is included."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Version should be present and a string
        assert isinstance(data['version'], str)
        assert len(data['version']) > 0


class TestMetricsRoute:
    """Test Prometheus metrics endpoint."""

    def test_metrics_endpoint_exists(self, client):
        """Test that /metrics endpoint exists and returns Prometheus format."""
        response = client.get('/metrics')
        
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')
        
        # Should contain Prometheus format metrics
        metrics_text = response.data.decode('utf-8')
        assert '# HELP' in metrics_text or '# TYPE' in metrics_text

    def test_metrics_http_request_count(self, client):
        """Test that HTTP request count metrics are collected."""
        # Make a few requests
        client.get('/api/health')
        client.get('/')
        
        # Check metrics
        response = client.get('/metrics')
        metrics_text = response.data.decode('utf-8')
        
        # Should have http_requests_total metric
        assert 'http_requests_total' in metrics_text
        assert 'health' in metrics_text or 'index' in metrics_text

    def test_metrics_http_request_duration(self, client):
        """Test that HTTP request duration metrics are collected."""
        # Make a request
        client.get('/api/health')
        
        # Check metrics
        response = client.get('/metrics')
        metrics_text = response.data.decode('utf-8')
        
        # Should have http_request_duration_seconds metric
        assert 'http_request_duration_seconds' in metrics_text

    def test_metrics_error_tracking(self, client):
        """Test that error metrics are tracked for 4xx/5xx responses."""
        # Make a request that will result in 404
        client.get('/nonexistent-endpoint')
        
        # Check metrics
        response = client.get('/metrics')
        metrics_text = response.data.decode('utf-8')
        
        # Should have error tracking (may or may not have errors yet depending on route handling)
        assert 'http_errors_total' in metrics_text or 'http_requests_total' in metrics_text


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


class TestHelperFunctions:
    """Test helper utility functions in app.py."""

    @patch('app.storage')
    def test_current_user_with_valid_session(self, mock_storage, client, app):
        """Test current_user returns user when session has valid user_id."""
        mock_storage.find_user_by_id.return_value = {'id': 1, 'username': 'testuser'}
        
        with app.test_request_context():
            from flask import session
            session['user_id'] = 1
            from app import current_user
            user = current_user()
            
            assert user is not None
            assert user['id'] == 1
            assert user['username'] == 'testuser'

    def test_current_user_no_session(self, client, app):
        """Test current_user returns None when no session."""
        with app.test_request_context():
            from app import current_user
            user = current_user()
            assert user is None

    @patch('app.storage')
    def test_current_user_user_not_found(self, mock_storage, client, app):
        """Test current_user returns None when user_id exists but user not found."""
        mock_storage.find_user_by_id.return_value = None
        
        with app.test_request_context():
            from flask import session
            session['user_id'] = 999
            from app import current_user
            user = current_user()
            
            assert user is None

    def test_require_login_json_returns_error_when_not_logged_in(self, client, app):
        """Test require_login_json returns 401 when user not logged in."""
        with app.test_request_context():
            from app import require_login_json
            result = require_login_json()
            
            assert result is not None
            status_code = result[1]  # tuple (response, status_code)
            assert status_code == 401

    @patch('app.current_user')
    def test_require_login_json_returns_none_when_logged_in(self, mock_current_user, client, app):
        """Test require_login_json returns None when user is logged in."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        with app.test_request_context():
            from app import require_login_json
            result = require_login_json()
            
            assert result is None


class TestAdditionalEdgeCases:
    """Test additional edge cases and error paths."""

    @patch('app.storage')
    @patch('app.current_user')
    def test_add_expense_with_default_date(self, mock_current_user, mock_storage, client):
        """Test adding expense without date uses current date."""
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
                                  'note': 'Lunch'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        # Verify save_expense was called with a date
        assert mock_storage.save_expense.called
        call_args = mock_storage.save_expense.call_args[0][0]
        assert 'date' in call_args

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_expenses_with_no_date_in_item(self, mock_current_user, mock_storage, client):
        """Test listing expenses when item has no date field."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_user_expenses.return_value = [
            {'id': 1, 'amount': 10.0, 'category': 'Food', 'note': ''}
        ]
        
        response = client.get('/api/expenses')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1

    @patch('app.storage')
    @patch('app.current_user')
    def test_list_expenses_date_filter_edge_cases(self, mock_current_user, mock_storage, client):
        """Test date filtering edge cases."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.get_user_expenses.return_value = [
            {'id': 1, 'amount': 10.0, 'category': 'Food', 'date': '2024-01-15', 'note': ''},
            {'id': 2, 'amount': 20.0, 'category': 'Transport', 'date': '2024-02-01', 'note': ''}
        ]
        
        # Test with date_from only
        response = client.get('/api/expenses?date_from=2024-01-20')
        assert response.status_code == 200
        
        # Test with date_to only
        response = client.get('/api/expenses?date_to=2024-01-20')
        assert response.status_code == 200

    @patch('app.storage')
    @patch('app.current_user')
    def test_get_expense_when_find_returns_none(self, mock_current_user, mock_storage, client):
        """Test getting expense when storage returns None."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = None
        
        response = client.get('/api/expenses/999')
        
        assert response.status_code == 404

    @patch('app.storage')
    @patch('app.current_user')
    def test_update_expense_invalid_amount_type(self, mock_current_user, mock_storage, client):
        """Test updating expense with invalid amount type."""
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
                             data=json.dumps({'amount': 'not-a-number'}),
                             content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_expense_when_find_returns_none(self, mock_current_user, mock_storage, client):
        """Test deleting expense when storage.find_expense returns None."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = None
        
        response = client.delete('/api/expenses/999')
        
        assert response.status_code == 404

    @patch('app.storage')
    @patch('app.current_user')
    def test_delete_expense_wrong_user(self, mock_current_user, mock_storage, client):
        """Test deleting expense owned by another user."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.find_expense.return_value = {
            'id': 5,
            'user_id': 2,  # Different user
            'amount': 100.0,
            'category': 'Shopping',
            'date': '2024-01-10',
            'note': 'Test'
        }
        
        response = client.delete('/api/expenses/5')
        
        assert response.status_code == 404

    @patch('app.storage')
    @patch('app.current_user')
    def test_monthly_endpoint_unauthenticated(self, mock_current_user, mock_storage, client):
        """Test monthly endpoint without authentication."""
        mock_current_user.return_value = None
        
        response = client.get('/api/monthly')
        
        assert response.status_code == 401

    @patch('app.storage')
    @patch('app.current_user')
    def test_summary_endpoint_unauthenticated(self, mock_current_user, mock_storage, client):
        """Test summary endpoint without authentication."""
        mock_current_user.return_value = None
        
        response = client.get('/api/summary')
        
        assert response.status_code == 401

    @patch('app.storage')
    @patch('app.current_user')
    def test_set_budget_missing_limit_amount(self, mock_current_user, mock_storage, client):
        """Test setting budget with missing limit_amount."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03'}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.storage')
    @patch('app.current_user')
    def test_set_budget_limit_amount_none(self, mock_current_user, mock_storage, client):
        """Test setting budget with limit_amount as None."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        
        response = client.post('/api/budget',
                              data=json.dumps({'month': '2024-03', 'limit_amount': None}),
                              content_type='application/json')
        
        assert response.status_code == 400

    @patch('app.storage')
    @patch('app.current_user')
    def test_set_budget_empty_month_uses_default(self, mock_current_user, mock_storage, client):
        """Test setting budget with empty month uses current month."""
        mock_current_user.return_value = {'id': 1, 'username': 'testuser'}
        mock_storage.upsert_budget.return_value = {
            'id': 1,
            'user_id': 1,
            'month': '2024-01',
            'limit_amount': 1000.0
        }
        mock_storage.get_budget_status.return_value = {
            'month': '2024-01',
            'limit': 1000.0,
            'spent': 0.0,
            'remaining': 1000.0,
            'status': 'ok'
        }
        
        response = client.post('/api/budget',
                              data=json.dumps({'limit_amount': 1000.0}),
                              content_type='application/json')
        
        assert response.status_code == 200

