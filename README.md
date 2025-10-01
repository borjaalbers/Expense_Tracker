# Expense Tracker - Full Stack Web Application

A modern, full-stack expense tracking application built with Flask and SQLite. Features user authentication, CRUD operations, data visualization, and responsive design.

##  Features

- **User Authentication**: Secure sign-up, sign-in, and session management
- **CRUD Operations**: Create, read, update, and delete expenses
- **Data Visualization**: Interactive pie charts (by category) and bar charts (monthly spending)
- **Responsive Design**: Modern UI with Bootstrap 5 and dark theme
- **Input Validation**: Prevents negative expenses and validates all inputs
- **Category Management**: Dropdown selection for expense categories
- **Real-time Updates**: Live data refresh and chart updates

##  Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite (file-based, no server required)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Authentication**: Flask sessions with password hashing

##  Requirements

- Python 3.9+
- pip (Python package manager)

##  Quick Setup (5 minutes)

### 1. Get the Code
```bash
# If you've already downloaded or cloned, cd into the project directory
cd Expense_Tracker-1
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python db_init.py
```

### 5. Run the Application
```bash
python app.py
```

### 6. Access the Application
Open your browser and navigate to: `http://localhost:5001`

##  How to Use

1. **Sign Up**: Create a new account on the landing page
2. **Sign In**: Use your credentials to access the dashboard
3. **Add Expenses**: Fill out amount, category, date, and note
4. **Personalize Categories**: Use the Add/Manage controls to add or remove categories; your dropdown updates automatically
5. **Monthly Budget**: Set a monthly limit (defaults to current month). The budget status and progress bar update automatically as you add/edit/delete expenses
6. **Scope Controls**: At the top of the dashboard, switch between Month or Year and click Apply to filter all lists and charts
7. **Analyze Spending**: View category summary (pie) and monthly totals (bar). Charts adapt to the selected scope
8. **Sign Out**: Use the sign-out button

##  Project Architecture

```
expense_tracker/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── storage_db.py          # Database operations (CRUD)
├── db.py                  # Database configuration
├── db_init.py             # Database initialization
├── requirements.txt       # Python dependencies
├── expense_tracker.db     # SQLite database file
├── templates/             # HTML templates
│   ├── layout.html        # Base template with navigation
│   ├── index.html         # Landing page (sign in/up)
│   └── dashboard.html     # Main dashboard (expenses, charts, budget, categories, scope)
├── static/                # Static assets
│   ├── app.js             # Frontend logic (CRUD, charts, budget, categories, scope)
│   └── styles.css         # Styles (dark theme + readability)
└── venv/                 # Python virtual environment
```

##  API Endpoints

### Authentication
- `POST /api/signup` - Create new user account
- `POST /api/signin` - User login
- `POST /api/signout` - User logout

### Expense Management
- `GET /api/expenses` - List all user expenses
- `POST /api/expenses` - Create new expense
- `GET /api/expenses/<id>` - Get specific expense
- `PUT /api/expenses/<id>` - Update expense
- `DELETE /api/expenses/<id>` - Delete expense

### Analytics
- `GET /api/summary` - Category totals for charts
- `GET /api/monthly` - Monthly spending totals

### Budget
- `GET /api/budget?month=YYYY-MM` - Get budget status for a month `{month, limit, spent, remaining, status}`
- `POST /api/budget` - Upsert a monthly budget `{month, limit_amount}`

### Categories
- `GET /api/categories` - List user categories (defaults are seeded on first access)
- `POST /api/categories` - Add a category `{name}` (idempotent)
- `DELETE /api/categories/<id>` - Remove a category by id

### Health Check
- `GET /api/health` - Application status

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password_hash` (Encrypted)

### Expenses Table
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `amount` (Float)
- `category` (String)
- `date` (Date)
- `note` (String)

### Budgets Table
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `month` (String YYYY-MM, unique per user)
- `limit_amount` (Float)

### Categories Table
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `name` (String, unique per user)

##  Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- User data isolation (users only see their own expenses)

##  Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern, professional appearance
- **Interactive Charts**: Real-time data visualization
- **Monthly Budgeting**: Set a monthly limit with live progress status and color feedback
- **Custom Categories**: Add/remove your own categories; dropdown stays in sync
- **Scope Controls**: Switch Month/Year at the top; all data and charts update
- **Form Validation**: Client-side and server-side validation
- **User Experience**: Smooth navigation and feedback

##  Running Tests

This project includes comprehensive backend unit tests with 90%+ code coverage.

### Install Test Dependencies
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage Report
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### View Coverage Report
```bash
# After running coverage, open the HTML report
open htmlcov/index.html
# On Windows: start htmlcov/index.html
# On Linux: xdg-open htmlcov/index.html
```

### Run Specific Test Files
```bash
pytest tests/test_models.py        # Test database models
pytest tests/test_storage_db.py    # Test storage layer
pytest tests/test_app.py           # Test Flask routes
```

### Coverage Target
- **Backend files**: 90%+ coverage
- **Files covered**: `app.py`, `models.py`, `storage_db.py`, `db.py`

##  Troubleshooting

### Port Already in Use
```bash
# Kill existing process
lsof -i:5001
kill [PID]

# Or use different port
PORT=5002 python app.py
```

### Database Issues
```bash
# Recreate database
rm expense_tracker.db
python db_init.py
```

### Dependencies Issues
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Smoke Test (optional)
With the server running in one terminal:
```bash
python test_sqlite_app.py
```

##  Future Enhancements

- **Budget Management**: Set monthly budgets and track progress (added)
- **Data Export**: Export expenses to CSV/PDF
- **Advanced Analytics**: Spending trends and predictions
- **Multi-currency Support**: Handle different currencies
- **Mobile App**: React Native or Flutter mobile version

##  Development Notes

This application follows modern web development practices:
- **Separation of Concerns**: Clear separation between frontend, backend, and database
- **RESTful API Design**: Standard HTTP methods and status codes
- **Responsive Design**: Mobile-first approach with Bootstrap
- **Security Best Practices**: Password hashing, input validation, session management
- **Code Organization**: Modular structure with clear file responsibilities

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
