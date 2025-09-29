# Expense Tracker - Full Stack Web Application

A modern, full-stack expense tracking application built with Flask and SQLite. Features user authentication, CRUD operations, data visualization, and responsive design.

## 🚀 Features

- **User Authentication**: Secure sign-up, sign-in, and session management
- **CRUD Operations**: Create, read, update, and delete expenses
- **Data Visualization**: Interactive pie charts (by category) and bar charts (monthly spending)
- **Responsive Design**: Modern UI with Bootstrap 5 and dark theme
- **Input Validation**: Prevents negative expenses and validates all inputs
- **Category Management**: Dropdown selection for expense categories
- **Real-time Updates**: Live data refresh and chart updates

## 🛠️ Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite (file-based, no server required)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Authentication**: Flask sessions with password hashing

## 📋 Requirements

- Python 3.9+
- pip (Python package manager)

## 🚀 Quick Setup (5 minutes)

### 1. Clone the Repository
```bash
git clone [your-repository-url]
cd expense_tracker
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

## 📖 How to Use

1. **Sign Up**: Create a new account on the landing page
2. **Sign In**: Use your credentials to access the dashboard
3. **Add Expenses**: Fill out the expense form with amount, category, date, and notes
4. **View Data**: See your expenses in the list with edit/delete options
5. **Analyze Spending**: View pie charts by category and bar charts by month
6. **Sign Out**: Use the sign-out button to end your session

## 🏗️ Project Architecture

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
│   ├── layout.html       # Base template with navigation
│   ├── index.html        # Landing page (sign in/up)
│   └── dashboard.html    # Main dashboard
├── static/               # Static assets
│   ├── app.js           # Frontend JavaScript
│   └── styles.css       # Custom CSS styling
└── venv/                 # Python virtual environment
```

## 🔧 API Endpoints

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

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- User data isolation (users only see their own expenses)

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern, professional appearance
- **Interactive Charts**: Real-time data visualization
- **Form Validation**: Client-side and server-side validation
- **User Experience**: Smooth navigation and feedback

## 🚨 Troubleshooting

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

## 🔮 Future Enhancements

- **Budget Management**: Set monthly budgets and track progress
- **Data Export**: Export expenses to CSV/PDF
- **Advanced Analytics**: Spending trends and predictions
- **Multi-currency Support**: Handle different currencies
- **Mobile App**: React Native or Flutter mobile version

## 📊 Development Notes

This application follows modern web development practices:
- **Separation of Concerns**: Clear separation between frontend, backend, and database
- **RESTful API Design**: Standard HTTP methods and status codes
- **Responsive Design**: Mobile-first approach with Bootstrap
- **Security Best Practices**: Password hashing, input validation, session management
- **Code Organization**: Modular structure with clear file responsibilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
