# Environment Configuration

This project relies on a handful of environment variables so that secrets and deployment-specific settings never ship inside the codebase. You can load them from a `.env` file for local development (e.g. using `python-dotenv`) or provide them via your process manager/hosting platform.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_SECRET_KEY` | ✅ | _(none)_ | Secret used by Flask sessions. Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` and keep private. |
| `DATABASE_URL` | ✅ | `sqlite:///expense_tracker.db` locally, `sqlite:////data/expense_tracker.db` in Docker/Render, `sqlite:////home/site/wwwroot/expense_tracker.db` on Azure App Service | SQLAlchemy database connection string. Swap to Azure Postgres/SQL in Branch 5.5. |
| `PORT` | ✅ | `5001` | Port Flask listens on. Render automatically maps `$PORT`; keep 5001 internally for Docker/local. |
| `DEFAULT_CATEGORIES` | Optional | `Food & Dining,...` | Comma-separated seed categories loaded into new accounts. Modify to add/remove defaults. |
| `FLASK_DEBUG` | Optional | `0` | Set to `1` for local debugging (auto reload) or `0` in hosted environments (Render). |

## Local Development

1. Copy `.env.example` to `.env`.
2. Customize values:
   ```bash
   cp .env.example .env
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # paste output as FLASK_SECRET_KEY inside .env
   ```
3. Export the values (or use a dotenv loader) before running `python app.py`.

## Render Deployment Steps (Environment Variables)

1. Open your Render service → **Settings → Environment**.
2. Ensure the following keys exist:
   - `FLASK_SECRET_KEY` → paste a generated secret (never commit it).
   - `DATABASE_URL` → `sqlite:////data/expense_tracker.db` for now.
   - `PORT` → `5001`.
   - `FLASK_DEBUG` → `0` (prevents the debugger from restarting the process).
3. Click **Save and deploy** so Render restarts with the updated configuration.
4. After deployment, hit `https://<service>.onrender.com/api/health` and review **Logs → Runtime** to confirm the server booted without warnings.

### Persistent Disk (Branch 5.5)

SQLite resets on every deployment unless you add a disk:

1. Render → **Settings → Disks → New Disk**.
2. Size ≥1 GB, mount path `/data`, attach to the web service.
3. Keep `DATABASE_URL=sqlite:////data/expense_tracker.db` (already documented). The app now auto-detects `/data` and writes there if `DATABASE_URL` is missing.
4. Recreate one user after the first restart; all future deploys keep the same database file on the disk.

If you later switch to Render PostgreSQL, swap `DATABASE_URL` to the Postgres URI and remove the disk (or keep it for backups).

## Rotating Secrets

- Regenerate `FLASK_SECRET_KEY` whenever credentials may have leaked. Update the value both in your `.env` file and on Render.
- If (in Branch 5.5) you switch to Render Postgres, replace `DATABASE_URL` with the connection string provided by Render (Format: `postgresql://USER:PASSWORD@HOST:PORT/DB`).

Keeping these values documented ensures local developers and Render stay in sync, satisfying Branch 5.3 requirements.

