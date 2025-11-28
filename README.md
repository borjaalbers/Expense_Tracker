# Expense Tracker - Full Stack Web Application

[![CI](https://github.com/borja/Expense_Tracker/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/borja/Expense_Tracker/actions/workflows/ci.yml)

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

## 🐳 Docker Deployment

### Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### Quick Start with Docker Compose

1. **Build and start the application:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   Open your browser and navigate to: `http://localhost:5001`

3. **Stop the application:**
   Press `Ctrl+C` in the terminal, or run:
   ```bash
   docker compose down
   ```

### Docker Build Instructions

**Build the Docker image:**
```bash
docker build -t expense-tracker .
```

**Run the container:**
```bash
docker run -p 5001:5001 \
  -e FLASK_SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:////data/expense_tracker.db \
  -v expense_data:/data \
  expense-tracker
```

### Docker Compose Usage

**Start services:**
```bash
docker compose up
```

**Start in detached mode (background):**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f
```

**Stop services:**
```bash
docker compose down
```

**Rebuild after code changes:**
```bash
docker compose up --build
```

**View running containers:**
```bash
docker compose ps
```

### Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET_KEY` | `dev-secret-key-change-me` | Secret key for Flask sessions (required in production) |
| `DATABASE_URL` | `sqlite:////data/expense_tracker.db` | Database connection URL |
| `PORT` | `5001` | Port on which the application runs |

**Setting environment variables:**

**With docker-compose:**
Create a `.env` file in the project root:
```env
FLASK_SECRET_KEY=your-production-secret-key-here
DATABASE_URL=sqlite:////data/expense_tracker.db
PORT=5001
```

**With docker run:**
```bash
docker run -p 5001:5001 \
  -e FLASK_SECRET_KEY=your-secret-key \
  -e PORT=5001 \
  expense-tracker
```

### Database Persistence

The application uses a Docker volume (`expense_data`) to persist the SQLite database. This ensures your data survives container restarts.

**View volume:**
```bash
docker volume ls
```

**Inspect volume:**
```bash
docker volume inspect expense_tracker_expense_data
```

**Remove volume (⚠️ deletes all data):**
```bash
docker compose down -v
```

## 🔐 Environment Variables

All required environment variables are documented in [`ENVIRONMENT.md`](ENVIRONMENT.md). For a quick start:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"  # generate FLASK_SECRET_KEY
```

Make sure the same keys exist on Render (Settings → Environment): `FLASK_SECRET_KEY`, `DATABASE_URL`, `PORT`, and `FLASK_DEBUG=0`.

## ☁️ Render Deployment (Docker Web Service)

The production instance runs on [Render](https://render.com) using the Dockerfile in this repo. Render builds the image automatically whenever `main` changes.

### Prerequisites
- Render account (free tier is fine; expect cold-start delay after inactivity)
- GitHub repository connected to Render
- Dockerfile present in repo (already provided)

### 1. Create or reuse the Web Service
1. Log into Render → **Dashboard → New → Web Service**.
2. Connect the `borjaalbers/Expense_Tracker` repository and select the `main` branch.
3. Choose **Docker** as the runtime (Render auto-detects the `Dockerfile`).
4. Set region closest to your users (current service lives in EU).
5. Keep the free instance plan unless you need faster cold starts.

Render uses the Dockerfile build instructions, so you can leave the build & start commands blank (Render runs `docker build` + `CMD ["python","app.py"]` from the image).

### 2. Configure environment variables
Navigate to **Settings → Environment** for the service and ensure:

| Key | Value |
|-----|-------|
| `FLASK_SECRET_KEY` | Paste a generated secret (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `DATABASE_URL` | `sqlite:////data/expense_tracker.db` (Docker volume managed by Render) |
| `PORT` | `5001` |
| `FLASK_DEBUG` | `0` |

Click **Save Changes** and then **Manual Deploy → Deploy latest commit** so the container restarts with the new settings.

### 3. Verify deployment
1. Open the public URL (e.g. `https://expense-tracker-8y4s.onrender.com`).
2. Hit `/api/health` to confirm a 200 response.
3. Sign up/in, add expenses, and check logs via **Logs → Live tail** if anything looks off.

### 4. Redeploy / roll back
- **Auto-deploy from main**: keep this enabled so every successful CI run ships automatically.
- **Manual redeploy**: use the **Manual Deploy** dropdown → *Deploy latest commit*.
- **Rollback**: go to **Events**, pick a previous successful deploy, and click **Rollback**.

### 5. Persist the database (Branch 5.5)
Without a persistent disk, every Render deploy wipes the in-container SQLite file and previously created accounts disappear. To keep data between deploys:

1. Render dashboard → your service → **Settings → Disks → New Disk**.
2. Name it (e.g., `expense-data`), size ≥1 GB, mount path `/data`, select **Delete mount directory contents** = No, then create.
3. Render restarts automatically. Ensure `DATABASE_URL` remains `sqlite:////data/expense_tracker.db` (already documented above).
4. After the restart, sign up once and your data will survive future deploys/CD runs.

> ℹ️ We prototyped Azure App Service during Branch 5, but the team decided to keep Render as the primary host to align with the already stable deployment. Azure notes remain in commit history for future work. If you later migrate to Render PostgreSQL, replace `DATABASE_URL` with the Postgres URI and run your migration script.

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

This project includes comprehensive backend tests (unit + integration) with 98% coverage and Ruff linting.

### Install Test Dependencies
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
pytest
```

### Run Lint (Ruff)
```bash
ruff check .
```

## Environment Variables & Secrets

| Variable | Required | Default | Description / Where to Set |
|----------|----------|---------|-----------------------------|
| `FLASK_SECRET_KEY` | ✅ | `dev-secret-key-change-me` | Flask session key. Store in `.env`, Render Environment, and GitHub Secrets. Rotate before production. |
| `DATABASE_URL` | ✅ (prod) | `sqlite:////data/expense_tracker.db` | SQLite for local/dev; set to Render Postgres URI (`postgres://...`) when using managed DB. |
| `PORT` | ➖ | `5001` | Local/server port; Render injects `$PORT` automatically but we pin to 5001 inside the container. |
| `FLASK_DEBUG` | ➖ | `1` | Force `0` in production to prevent reload loops (Render/Azure). |
| `PGSSLMODE` | ➖ | `disable` | Set to `require` when using Render Postgres so SQLAlchemy negotiates TLS. |
| `DEFAULT_CATEGORIES` | ➖ | Built-in list | Customize seeded categories via comma-separated string. |
| `RENDER_DEPLOY_HOOK` | ✅ (CD) | — | GitHub secret used by `.github/workflows/cd-render.yml` to trigger redeploys. Never commit the URL. |

**Local development**
1. Copy `.env.example` → `.env`
2. Populate keys (`FLASK_SECRET_KEY`, optional `DATABASE_URL`, etc.)
3. `source .env` (macOS/Linux) or use your IDE/terminal env var support

**GitHub Actions / Deployment**
- Add the same secrets under *Settings → Secrets and variables → Actions* (e.g., `FLASK_SECRET_KEY`, `DATABASE_URL`, `RENDER_DEPLOY_HOOK`)
- The CI workflow automatically exports them when present, keeping sensitive values out of the repo
- Render → Settings → Environment: mirror `.env` keys plus `PGSSLMODE=require`. Documented exhaustively in `ENVIRONMENT.md`.

##  CI/CD Pipeline

- **GitHub Actions**: `.github/workflows/ci.yml` runs on every `push`, `pull_request`, and manual `workflow_dispatch`.
- **Test job**: Matrix across Python 3.9–3.11 installs deps, runs Ruff lint, executes unit + integration tests with coverage enforcement (`--cov-fail-under=70`), and uploads the HTML coverage report as an artifact.
- **Build job**: Runs after tests to install dependencies on Python 3.11, import critical modules (`app`, `storage_db`), and perform a lightweight configuration sanity check so the pipeline fails if the app cannot start.
- **Badges & artifacts**: The badge above reflects the latest CI status; download `htmlcov` artifacts from the Actions tab for coverage inspection.

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
- **Backend files**: 98% coverage
- **Files covered**: `app.py`, `models.py`, `storage_db.py`, `db.py`

##  CI/CD

- **Continuous Integration**: `.github/workflows/ci.yml` (matrix across Python versions, installs deps, runs lint/tests, enforces coverage, and publishes reports). Triggered on every `push`, `pull_request`, or manual `workflow_dispatch`.
- **Continuous Deployment**: `.github/workflows/cd-render.yml` triggers whenever `main` is updated (or via manual dispatch). It POSTs to Render’s Deploy Hook so the Docker Web Service redeploys the latest image. Store the hook URL as a GitHub secret named `RENDER_DEPLOY_HOOK`. Rotate the hook in Render → Settings → Deploy Hooks if it ever leaks.
- **Rollback flow**: Use Render’s Events tab to redeploy a previous successful image; CI continues to guard future pushes.
- **Verification gates**: After each deploy we run the manual checklist below (sign in/out, CRUD, budget, categories, `/api/health`, `/metrics`, persistence) and keep screenshots under `docs/screenshots/render-verification/` for auditing.

## 📈 Monitoring & Observability

- `/api/health` now returns service status, DB connectivity, uptime, and git SHA metadata. Render health checks point here (Settings → Health Check Path).
- `/metrics` exposes Prometheus counters/histograms via `prometheus-client` for request count, latency, and error tracking. Curl it directly or point Prometheus at it.
- **Local Prometheus + Grafana stack**
  1. `docker compose -f docker-compose.monitoring.yml up`
  2. Prometheus scrapes the Flask container via `prometheus.yml`
  3. Grafana auto-imports `grafana/dashboards/expense-tracker.json` so you can see request rate, p95 latency, error % and active sessions.
- Export screenshots or tweak the dashboard before submitting the assignment; Grafana credentials + port mappings live in `docker-compose.monitoring.yml`.

## ✅ Deployment Verification Checklist (Branch 5.6)

We validate every production redeploy using the same steps referenced in `IMPLEMENTATION_PLAN.md`:

1. Sign up, sign in, sign out.
2. Create/edit/delete expenses and verify both dashboard tables and charts reflect the change.
3. Update the monthly budget and inspect the status banner.
4. Add/delete categories and confirm dropdown sync.
5. Hit `/api/health` and `/metrics` for HTTP 200 responses.
6. Run the GitHub `cd-render` workflow, wait for Render to redeploy, then repeat 1–4 to confirm persisted data.

Screenshots for the latest run live in `docs/screenshots/render-verification/` and can be re-generated using the links listed in `IMPLEMENTATION_PLAN.md`.

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

**Render/Postgres tips**
- If the service is stuck on “Deploying…”, open **Logs → Live** and confirm the Docker image built successfully. Cold starts on the free tier can take ~2 minutes.
- When switching from SQLite to Render Postgres, update `DATABASE_URL`, set `PGSSLMODE=require`, redeploy, then run `python db_init.py` locally with the Postgres URL to run migrations.
- The free tier does not support persistent disks; use the managed Postgres service (Branch 5.5) for durable data.

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

## 🗂️ Documentation & Reports

- `IMPLEMENTATION_PLAN.md` – branch-by-branch checklist plus Render verification evidence.
- `ENVIRONMENT.md` – definitive guide to every environment variable (local, CI, Render).
- `REPORT.md` – 5–6 page narrative summarizing all DevOps improvements (required deliverable).
- `docs/screenshots/render-verification/` – screenshot set referenced in Branch 5.6 and the report.

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
