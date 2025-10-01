# Backend Unit Tests

This directory contains comprehensive unit tests for the Expense Tracker backend with **93% overall coverage**.

## Quick Start

```bash
# Install dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## Test Files

### conftest.py
Shared fixtures and configuration:
- In-memory SQLite database per test
- Flask test client
- Sample user and expense fixtures

### test_models.py (11 tests)
Tests for SQLAlchemy models:
- User, Expense, Budget, Category models
- Unique constraints validation
- Relationships and cascade delete behavior
- Multi-user data isolation

### test_storage_db.py (38 tests)
Tests for storage layer:
- User CRUD operations
- Expense CRUD with user isolation
- Analytics (summary, monthly totals)
- Budget management (create, update, status)
- Category management (list, add, delete, defaults)
- Edge cases (not found, wrong user, validation)
- Budget status calculations (ok, warning, over)

### test_app.py (48 tests)
Tests for Flask routes:
- Authentication (signup, signin, signout)
- Expense API endpoints (CRUD + filtering)
- Budget API endpoints (get, set, validation)
- Category API endpoints (list, add, delete)
- Analytics endpoints (summary, monthly)
- Page routing and redirects
- Authentication enforcement
- Input validation (amounts, dates, formats)
- Error handling (400, 401, 404, 500)

### test_db.py (7 tests)
Tests for database configuration:
- Database URL generation (default + env var)
- SQLAlchemy engine creation
- Session factory
- Context manager behavior (commit/rollback)

## Coverage Results

**Overall: 93% backend coverage** 

| Module | Statements | Missed | Coverage |
|--------|-----------|--------|----------|
| **models.py** | 37 | 0 | **100%**  |
| **db.py** | 21 | 0 | **100%**  |
| **storage_db.py** | 142 | 8 | **94%**  |
| **app.py** | 251 | 22 | **91%**  |
| **Total** | **451** | **30** | **93%**  |

**All 99 tests passing** 

## Writing New Tests

Follow the existing patterns:
1. Use fixtures from conftest.py
2. Mock external dependencies
3. Test both success and error cases
4. Use descriptive test names
5. Add docstrings explaining what's being tested

Example:
```python
@patch('app.storage')
@patch('app.current_user')
def test_feature_success(self, mock_current_user, mock_storage, client):
    """Test successful feature execution."""
    # Setup
    mock_current_user.return_value = {'id': 1, 'username': 'test'}
    mock_storage.method.return_value = expected_result
    
    # Execute
    response = client.post('/api/endpoint', json=data)
    
    # Assert
    assert response.status_code == 200
```

## Continuous Integration

These tests are designed to run in CI/CD:
- Fast execution (~1 second)
- No external dependencies
- Clear exit codes
- Coverage reports generated

