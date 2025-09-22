# Expense Tracker (Flask) – Easy Setup & Usage Guide

## What this app does
Track personal expenses with per-user accounts. After you sign up or sign in, you can add, view, edit, and delete your own expenses. The dashboard shows:
- By-category totals (pie chart)
- Monthly totals (bar chart)

Data is stored in simple JSON files: `users.json` and `expenses.json`.

## Tech stack
- Backend: Flask (Python)
- Storage: JSON files (no database required)
- Frontend: HTML/CSS + vanilla JS + Chart.js (from CDN)

## Requirements
- Python 3.9+
- pip (comes with most Python installs)

## Quick start (2 minutes)
1) Clone and open this folder in a terminal.

2) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
On Windows (PowerShell):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) (Optional but recommended) Set a secret key for sessions:
```bash
export FLASK_SECRET_KEY="change-this-to-a-long-random-string"
```
On Windows (Powershell):
```powershell
$env:FLASK_SECRET_KEY = "change-this-to-a-long-random-string"
```

5) Run the app:
```bash
python app.py
```

6) Open the app: `http://localhost:5000`

You should see a Sign in / Sign up page. Create an account and you’ll be redirected to the dashboard.

## How to use the app
- Sign up or Sign in on `/`.
- On `/dashboard`:
  - Add an expense with Amount, Category, Date (optional), and Note (optional).
  - View your expenses in the table. Use Edit or Delete to modify them.
  - See charts update live: By Category (pie) and Monthly Totals (bar).
- Use the Sign out button at the top right to log out.

## Project structure
```text
expense_tracker/
  app.py                # Flask app and API routes
  storage.py            # JSON file read/write and aggregations
  users.json            # Created automatically on first run (user records)
  expenses.json         # Created automatically on first run (expenses per user)
  requirements.txt      # Python dependencies
  templates/
    layout.html         # Base layout
    index.html          # Sign in / Sign up page
    dashboard.html      # Dashboard page (charts + table)
  static/
    app.js              # Frontend logic and API calls
```

## Configuration
- `FLASK_SECRET_KEY`: Secret used to sign the user session.
  - Default in dev: `dev-secret-key-change-me` (do not use in production).
  - Set an environment variable to override.

## API reference (for devs)
All responses are JSON. Most endpoints require you to be signed in (session cookie).

- Auth
  - `POST /api/signup`
    - Body: `{ "username": "alice", "password": "secret" }`
    - 201 Created → `{ message, user: { id, username } }`
  - `POST /api/signin`
    - Body: `{ "username": "alice", "password": "secret" }`
    - 200 OK → `{ message, user }`
  - `POST /api/signout`
    - 200 OK → `{ message }`

- Expenses
  - `POST /api/expenses`
    - Body: `{ amount: number, category: string, date?: "YYYY-MM-DD", note?: string }`
    - 201 Created → full expense object `{ id, user_id, amount, category, date, note }`
  - `GET /api/expenses`
    - Optional query: `category`, `date_from`, `date_to` (strings like `YYYY-MM-DD`)
    - 200 OK → `[ ...expenses sorted by date desc... ]`
  - `PUT /api/expenses/<id>`
    - Body: any of `{ amount, category, date, note }`
    - 200 OK → updated expense
  - `DELETE /api/expenses/<id>`
    - 200 OK → `{ deleted: <id> }`

- Stats
  - `GET /api/summary` → `{ "Category": total, ... }`
  - `GET /api/monthly` → `{ "YYYY-MM": total, ... }` (sorted ascending)

- Health
  - `GET /api/health` → `{ status: "ok", user: <username|null> }`

### Example curl calls
Sign up:
```bash
curl -i -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret"}' \
  http://localhost:5000/api/signup
```
Add an expense:
```bash
curl -i -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"amount":12.5,"category":"Food","date":"2025-09-22","note":"Lunch"}' \
  http://localhost:5000/api/expenses
```
List expenses:
```bash
curl -s -b cookies.txt http://localhost:5000/api/expenses | jq
```

## Data & persistence
- Files live next to the app in this folder:
  - `users.json`: list of `{ id, username, password_hash }`
  - `expenses.json`: list of `{ id, user_id, amount, category, date, note }`
- Files are created automatically if missing. If a file is corrupted, it will reset to an empty list on the next write.

## Troubleshooting
- Port already in use (5000):
  - Change port: `PORT=5050 python app.py`
- Can’t sign in after sign up:
  - Restart the server and try again. Ensure cookies are enabled.
- Charts not showing:
  - Check console errors (Chart.js requires internet for the CDN). Verify `/api/summary` and `/api/monthly` return data while signed in.
- JSON files permission issues:
  - Ensure you have write access to the project folder.

## Notes for production (if you deploy)
- Set a strong `FLASK_SECRET_KEY`.
- Put the app behind a proper WSGI server (e.g., gunicorn) and a reverse proxy.
- Move storage to a real database (SQLite/Postgres) for concurrency and reliability.
- Add HTTPS and user/password policies.

---

Happy tracking! If you get stuck, open an issue or ask for help.
