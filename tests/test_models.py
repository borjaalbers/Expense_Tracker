"""
Unit tests for SQLAlchemy models.
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from models import User, Expense, Budget, Category


class TestUserModel:
    """Test User model constraints and relationships."""

    def test_create_user(self, test_db_session):
        """Test creating a valid user."""
        user = User(username='john', password_hash='hashed_pw')
        test_db_session.add(user)
        test_db_session.commit()
        
        assert user.id is not None
        assert user.username == 'john'
        assert user.password_hash == 'hashed_pw'

    def test_username_unique_constraint(self, test_db_session):
        """Test that duplicate usernames are not allowed."""
        user1 = User(username='duplicate', password_hash='pw1')
        test_db_session.add(user1)
        test_db_session.commit()
        
        user2 = User(username='duplicate', password_hash='pw2')
        test_db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()

    def test_user_expenses_relationship(self, test_db_session):
        """Test one-to-many relationship between User and Expense."""
        user = User(username='alice', password_hash='pw')
        test_db_session.add(user)
        test_db_session.commit()
        
        expense1 = Expense(user_id=user.id, amount=10.0, category='Test', date=date.today(), note='')
        expense2 = Expense(user_id=user.id, amount=20.0, category='Test', date=date.today(), note='')
        test_db_session.add_all([expense1, expense2])
        test_db_session.commit()
        
        test_db_session.refresh(user)
        assert len(user.expenses) == 2


class TestExpenseModel:
    """Test Expense model constraints and relationships."""

    def test_create_expense(self, test_db_session, sample_user):
        """Test creating a valid expense."""
        expense = Expense(
            user_id=sample_user.id,
            amount=99.99,
            category='Shopping',
            date=date(2024, 2, 10),
            note='Test purchase'
        )
        test_db_session.add(expense)
        test_db_session.commit()
        
        assert expense.id is not None
        assert expense.user_id == sample_user.id
        assert expense.amount == 99.99
        assert expense.category == 'Shopping'
        assert expense.note == 'Test purchase'

    def test_expense_user_relationship(self, test_db_session, sample_user):
        """Test back-reference from Expense to User."""
        expense = Expense(
            user_id=sample_user.id,
            amount=50.0,
            category='Food',
            date=date.today(),
            note=''
        )
        test_db_session.add(expense)
        test_db_session.commit()
        test_db_session.refresh(expense)
        
        assert expense.user.id == sample_user.id
        assert expense.user.username == sample_user.username

    def test_expense_cascade_delete(self, test_db_session, sample_user):
        """Test that deleting a user cascades to expenses."""
        expense = Expense(user_id=sample_user.id, amount=10.0, category='Test', date=date.today(), note='')
        test_db_session.add(expense)
        test_db_session.commit()
        
        test_db_session.delete(sample_user)
        test_db_session.commit()
        
        # Expense should be deleted
        from sqlalchemy import select
        result = test_db_session.execute(select(Expense).where(Expense.id == expense.id)).scalar_one_or_none()
        assert result is None


class TestBudgetModel:
    """Test Budget model constraints."""

    def test_create_budget(self, test_db_session, sample_user):
        """Test creating a valid budget."""
        budget = Budget(user_id=sample_user.id, month='2024-03', limit_amount=1000.0)
        test_db_session.add(budget)
        test_db_session.commit()
        
        assert budget.id is not None
        assert budget.user_id == sample_user.id
        assert budget.month == '2024-03'
        assert budget.limit_amount == 1000.0

    def test_budget_unique_user_month(self, test_db_session, sample_user):
        """Test that a user can't have duplicate budgets for the same month."""
        budget1 = Budget(user_id=sample_user.id, month='2024-04', limit_amount=500.0)
        test_db_session.add(budget1)
        test_db_session.commit()
        
        budget2 = Budget(user_id=sample_user.id, month='2024-04', limit_amount=600.0)
        test_db_session.add(budget2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()


class TestCategoryModel:
    """Test Category model constraints."""

    def test_create_category(self, test_db_session, sample_user):
        """Test creating a valid category."""
        category = Category(user_id=sample_user.id, name='Custom Category')
        test_db_session.add(category)
        test_db_session.commit()
        
        assert category.id is not None
        assert category.user_id == sample_user.id
        assert category.name == 'Custom Category'

    def test_category_unique_user_name(self, test_db_session, sample_user):
        """Test that a user can't have duplicate category names."""
        cat1 = Category(user_id=sample_user.id, name='Travel')
        test_db_session.add(cat1)
        test_db_session.commit()
        
        cat2 = Category(user_id=sample_user.id, name='Travel')
        test_db_session.add(cat2)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()

    def test_different_users_same_category_name(self, test_db_session):
        """Test that different users can have the same category name."""
        from werkzeug.security import generate_password_hash
        
        user1 = User(username='user1', password_hash=generate_password_hash('pw'))
        user2 = User(username='user2', password_hash=generate_password_hash('pw'))
        test_db_session.add_all([user1, user2])
        test_db_session.commit()
        
        cat1 = Category(user_id=user1.id, name='Travel')
        cat2 = Category(user_id=user2.id, name='Travel')
        test_db_session.add_all([cat1, cat2])
        test_db_session.commit()
        
        # Should succeed - different users
        assert cat1.id is not None
        assert cat2.id is not None

