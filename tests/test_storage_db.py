"""
Unit tests for storage_db.py data access layer.
"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from models import User, Expense, Budget, Category
import storage_db


class TestUserStorage:
    """Test user storage functions."""

    @patch('storage_db.get_session')
    def test_save_user(self, mock_get_session):
        """Test saving a new user."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'newuser'
        mock_user.password_hash = 'hashed'
        
        def side_effect_add(obj):
            obj.id = 1
        
        mock_session.add.side_effect = side_effect_add
        
        result = storage_db.save_user({'username': 'newuser', 'password_hash': 'hashed'})
        
        assert mock_session.add.called
        assert mock_session.flush.called

    @patch('storage_db.get_session')
    def test_find_user_by_username_found(self, mock_get_session):
        """Test finding an existing user by username."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.password_hash = 'hashed'
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = storage_db.find_user_by_username('testuser')
        
        assert result is not None
        assert result['username'] == 'testuser'
        assert result['id'] == 1

    @patch('storage_db.get_session')
    def test_find_user_by_username_not_found(self, mock_get_session):
        """Test finding a non-existent user."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = storage_db.find_user_by_username('nonexistent')
        
        assert result is None

    @patch('storage_db.get_session')
    def test_find_user_by_id(self, mock_get_session):
        """Test finding user by ID."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.username = 'iduser'
        mock_user.password_hash = 'hashed'
        
        mock_session.get.return_value = mock_user
        
        result = storage_db.find_user_by_id(5)
        
        assert result is not None
        assert result['id'] == 5
        assert result['username'] == 'iduser'


class TestExpenseStorage:
    """Test expense storage functions."""

    @patch('storage_db.get_session')
    def test_save_expense(self, mock_get_session):
        """Test saving a new expense."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        expense_data = {
            'user_id': 1,
            'amount': 100.0,
            'category': 'Food',
            'date': '2024-01-15',
            'note': 'Lunch'
        }
        
        result = storage_db.save_expense(expense_data)
        
        assert mock_session.add.called
        assert mock_session.flush.called

    @patch('storage_db.get_session')
    def test_find_expense(self, mock_get_session):
        """Test finding an expense by ID."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_expense = MagicMock()
        mock_expense.id = 10
        mock_expense.user_id = 1
        mock_expense.amount = 50.0
        mock_expense.category = 'Transport'
        mock_expense.date = date(2024, 2, 1)
        mock_expense.note = 'Taxi'
        
        mock_session.get.return_value = mock_expense
        
        result = storage_db.find_expense(10)
        
        assert result is not None
        assert result['id'] == 10
        assert result['amount'] == 50.0

    @patch('storage_db.get_session')
    def test_find_expense_not_found(self, mock_get_session):
        """Test finding a non-existent expense."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.get.return_value = None
        
        result = storage_db.find_expense(999)
        
        assert result is None

    @patch('storage_db.get_session')
    def test_get_user_expenses(self, mock_get_session):
        """Test retrieving all expenses for a user."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_exp1 = MagicMock()
        mock_exp1.id = 1
        mock_exp1.user_id = 1
        mock_exp1.amount = 10.0
        mock_exp1.category = 'Food'
        mock_exp1.date = date(2024, 1, 1)
        mock_exp1.note = 'A'
        
        mock_exp2 = MagicMock()
        mock_exp2.id = 2
        mock_exp2.user_id = 1
        mock_exp2.amount = 20.0
        mock_exp2.category = 'Shopping'
        mock_exp2.date = date(2024, 1, 2)
        mock_exp2.note = 'B'
        
        mock_session.scalars.return_value.all.return_value = [mock_exp1, mock_exp2]
        
        result = storage_db.get_user_expenses(1)
        
        assert len(result) == 2
        assert result[0]['amount'] == 10.0
        assert result[1]['amount'] == 20.0

    @patch('storage_db.get_session')
    def test_update_expense(self, mock_get_session):
        """Test updating an expense."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_expense = MagicMock()
        mock_expense.id = 5
        mock_expense.user_id = 1
        mock_expense.amount = 100.0
        mock_expense.category = 'Food'
        mock_expense.date = date(2024, 1, 10)
        mock_expense.note = 'Old note'
        
        mock_session.get.return_value = mock_expense
        
        updates = {'amount': 150.0, 'note': 'Updated note'}
        result = storage_db.update_expense(5, updates)
        
        assert mock_session.flush.called
        assert result is not None

    @patch('storage_db.get_session')
    def test_delete_expense(self, mock_get_session):
        """Test deleting an expense."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_expense = MagicMock()
        mock_session.get.return_value = mock_expense
        
        result = storage_db.delete_expense(5)
        
        assert mock_session.delete.called
        assert result is True

    @patch('storage_db.get_session')
    def test_delete_expense_not_found(self, mock_get_session):
        """Test deleting a non-existent expense."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.get.return_value = None
        
        result = storage_db.delete_expense(999)
        
        assert result is False


class TestAnalyticsStorage:
    """Test analytics and summary functions."""

    @patch('storage_db.get_session')
    def test_summary_by_category(self, mock_get_session):
        """Test category summary aggregation."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.all.return_value = [
            ('Food', 100.0),
            ('Transport', 50.0),
        ]
        
        result = storage_db.summary_by_category(1)
        
        assert 'Food' in result
        assert result['Food'] == 100.0
        assert result['Transport'] == 50.0

    @patch('storage_db.get_session')
    def test_monthly_totals(self, mock_get_session):
        """Test monthly totals aggregation."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.all.return_value = [
            ('2024-01', 200.0),
            ('2024-02', 150.0),
        ]
        
        result = storage_db.monthly_totals(1)
        
        assert '2024-01' in result
        assert result['2024-01'] == 200.0
        assert result['2024-02'] == 150.0


class TestBudgetStorage:
    """Test budget storage functions."""

    @patch('storage_db.get_session')
    def test_get_budget(self, mock_get_session):
        """Test retrieving a budget."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_budget = MagicMock()
        mock_budget.id = 1
        mock_budget.user_id = 1
        mock_budget.month = '2024-03'
        mock_budget.limit_amount = 1000.0
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_budget
        
        result = storage_db.get_budget(1, '2024-03')
        
        assert result is not None
        assert result['month'] == '2024-03'
        assert result['limit_amount'] == 1000.0

    @patch('storage_db.get_session')
    def test_get_budget_not_found(self, mock_get_session):
        """Test retrieving a non-existent budget."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = storage_db.get_budget(1, '2024-99')
        
        assert result is None

    @patch('storage_db.get_session')
    def test_upsert_budget_create(self, mock_get_session):
        """Test creating a new budget."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = storage_db.upsert_budget(1, '2024-05', 500.0)
        
        assert mock_session.add.called
        assert mock_session.flush.called

    @patch('storage_db.get_session')
    @patch('storage_db.monthly_totals')
    @patch('storage_db.get_budget')
    def test_get_budget_status_with_budget(self, mock_get_budget, mock_monthly_totals, mock_get_session):
        """Test budget status calculation when budget exists."""
        mock_get_budget.return_value = {
            'id': 1,
            'user_id': 1,
            'month': '2024-03',
            'limit_amount': 1000.0
        }
        mock_monthly_totals.return_value = {'2024-03': 300.0}
        
        result = storage_db.get_budget_status(1, '2024-03')
        
        assert result['month'] == '2024-03'
        assert result['limit'] == 1000.0
        assert result['spent'] == 300.0
        assert result['remaining'] == 700.0
        assert result['status'] == 'ok'

    @patch('storage_db.monthly_totals')
    @patch('storage_db.get_budget')
    def test_get_budget_status_no_budget(self, mock_get_budget, mock_monthly_totals):
        """Test budget status when no budget is set."""
        mock_get_budget.return_value = None
        mock_monthly_totals.return_value = {'2024-03': 100.0}
        
        result = storage_db.get_budget_status(1, '2024-03')
        
        assert result['month'] == '2024-03'
        assert result['limit'] is None
        assert result['spent'] == 100.0
        assert result['remaining'] is None
        assert result['status'] == 'no_budget'


class TestCategoryStorage:
    """Test category storage functions."""

    @patch('storage_db._ensure_default_categories')
    @patch('storage_db.get_session')
    def test_list_categories(self, mock_get_session, mock_ensure):
        """Test listing categories."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_cat1 = MagicMock()
        mock_cat1.id = 1
        mock_cat1.name = 'Food'
        
        mock_cat2 = MagicMock()
        mock_cat2.id = 2
        mock_cat2.name = 'Transport'
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_cat1, mock_cat2]
        
        result = storage_db.list_categories(1)
        
        assert len(result) == 2
        assert result[0]['name'] == 'Food'
        assert result[1]['name'] == 'Transport'

    @patch('storage_db.get_session')
    def test_add_category(self, mock_get_session):
        """Test adding a new category."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = storage_db.add_category(1, 'Custom')
        
        assert mock_session.add.called
        assert mock_session.flush.called

    def test_add_category_empty_name(self):
        """Test adding category with empty name raises ValueError."""
        with pytest.raises(ValueError):
            storage_db.add_category(1, '')

    def test_add_category_whitespace_name(self):
        """Test adding category with whitespace-only name raises ValueError."""
        with pytest.raises(ValueError):
            storage_db.add_category(1, '   ')

    @patch('storage_db.get_session')
    def test_add_category_duplicate(self, mock_get_session):
        """Test adding a duplicate category returns existing."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_existing = MagicMock()
        mock_existing.id = 5
        mock_existing.name = 'Custom'
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_existing
        
        result = storage_db.add_category(1, 'Custom')
        
        assert result['id'] == 5
        assert result['name'] == 'Custom'

    @patch('storage_db.get_session')
    def test_delete_category(self, mock_get_session):
        """Test deleting a category."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_category = MagicMock()
        mock_category.user_id = 1
        mock_session.get.return_value = mock_category
        
        result = storage_db.delete_category(1, 5)
        
        assert mock_session.delete.called
        assert result is True

    @patch('storage_db.get_session')
    def test_delete_category_not_found(self, mock_get_session):
        """Test deleting a non-existent category."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.get.return_value = None
        
        result = storage_db.delete_category(1, 999)
        
        assert result is False

    @patch('storage_db.get_session')
    def test_delete_category_wrong_user(self, mock_get_session):
        """Test deleting a category owned by another user."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_category = MagicMock()
        mock_category.user_id = 2  # Different user
        mock_session.get.return_value = mock_category
        
        result = storage_db.delete_category(1, 5)
        
        assert result is False


class TestStorageEdgeCases:
    """Test additional edge cases and paths."""

    @patch('storage_db.get_session')
    def test_get_all_users(self, mock_get_session):
        """Test retrieving all users."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.password_hash = 'hashed'
        
        mock_session.scalars.return_value.all.return_value = [mock_user]
        
        result = storage_db.get_all_users()
        
        assert len(result) == 1
        assert result[0]['username'] == 'testuser'

    @patch('storage_db.get_session')
    def test_get_all_expenses(self, mock_get_session):
        """Test retrieving all expenses."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_exp = MagicMock()
        mock_exp.id = 1
        mock_exp.user_id = 1
        mock_exp.amount = 10.0
        mock_exp.category = 'Food'
        mock_exp.date = date(2024, 1, 1)
        mock_exp.note = 'Test'
        
        mock_session.scalars.return_value.all.return_value = [mock_exp]
        
        result = storage_db.get_all_expenses()
        
        assert len(result) == 1
        assert result[0]['amount'] == 10.0

    @patch('storage_db.get_session')
    def test_update_expense_not_found(self, mock_get_session):
        """Test updating non-existent expense returns None."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.get.return_value = None
        
        result = storage_db.update_expense(999, {'amount': 100})
        
        assert result is None

    @patch('storage_db.get_session')
    def test_update_expense_with_date(self, mock_get_session):
        """Test updating expense with date conversion."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_expense = MagicMock()
        mock_expense.id = 5
        mock_expense.user_id = 1
        mock_expense.amount = 100.0
        mock_expense.category = 'Food'
        mock_expense.date = date(2024, 1, 10)
        mock_expense.note = 'Old'
        
        mock_session.get.return_value = mock_expense
        
        result = storage_db.update_expense(5, {'date': '2024-02-01', 'note': 'New'})
        
        assert mock_session.flush.called

    @patch('storage_db.get_budget')
    @patch('storage_db.monthly_totals')
    def test_get_budget_status_over_budget(self, mock_monthly, mock_budget):
        """Test budget status when over limit."""
        mock_budget.return_value = {
            'id': 1,
            'user_id': 1,
            'month': '2024-03',
            'limit_amount': 100.0
        }
        mock_monthly.return_value = {'2024-03': 150.0}
        
        result = storage_db.get_budget_status(1, '2024-03')
        
        assert result['status'] == 'over'
        assert result['remaining'] == 0.0

    @patch('storage_db.get_budget')
    @patch('storage_db.monthly_totals')
    def test_get_budget_status_warning(self, mock_monthly, mock_budget):
        """Test budget status when at warning threshold (90%)."""
        mock_budget.return_value = {
            'id': 1,
            'user_id': 1,
            'month': '2024-03',
            'limit_amount': 1000.0
        }
        mock_monthly.return_value = {'2024-03': 920.0}
        
        result = storage_db.get_budget_status(1, '2024-03')
        
        assert result['status'] == 'warning'

    @patch('storage_db.get_session')
    def test_upsert_budget_update_existing(self, mock_get_session):
        """Test updating an existing budget."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_budget = MagicMock()
        mock_budget.id = 1
        mock_budget.user_id = 1
        mock_budget.month = '2024-03'
        mock_budget.limit_amount = 500.0
        
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_budget
        
        result = storage_db.upsert_budget(1, '2024-03', 1000.0)
        
        assert mock_session.flush.called
        # Should update, not add
        assert not mock_session.add.called

