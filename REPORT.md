# Expense Tracker – DevOps Improvement Report

> Prepared for “Improve and Automate Your Application with DevOps Practices” (Assignment 2) – November 2025

---

## 1. Introduction

Assignment 2 builds on the Expense Tracker application from Assignment 1 by applying end-to-end DevOps practices: refactoring for maintainability, adding automated tests, wiring continuous integration, containerizing the runtime, deploying to a managed platform, and instrumenting production health. This document summarizes the work completed across Branches 1–6 (code, tests, CI, Docker, deployment, monitoring) and explains how the project now satisfies the rubric requirements:

- **Code Quality & Refactoring (25 %)** – systematized configuration, modularized business logic, removed duplication.
- **Testing & Coverage (20 %)** – comprehensive unit + integration suites with 98 % backend coverage and HTML reports.
- **CI/CD Pipeline (20 %)** – GitHub Actions for test/coverage enforcement plus Render deploy automation via deploy hooks.
- **Deployment & Containerization (20 %)** – hardened Dockerfile, Docker Compose, and Render Web Service backed by managed Postgres.
- **Monitoring & Documentation (15 %)** – enhanced `/api/health`, new `/metrics`, Prometheus/Grafana setup, README/ENVIRONMENT.md/IMPLEMENTATION_PLAN.md updates, and this report.

Each section below calls out the original problems, the solutions that were implemented, trade-offs considered, and verification evidence (tests, screenshots, logs).

---

## 2. Code Quality and Refactoring

### 2.1 Configuration Management
- Introduced `config.py` to centralize Flask secrets, database URLs, default categories, and port settings.
- Adopted environment-variable-first configuration, so production secrets live in Render/GitHub while local `.env` files provide fallbacks.
- Eliminated hard-coded magic numbers and strings (e.g., default categories, secret keys) from route handlers.

### 2.2 Application Structure
- Broke down `app.py` by extracting validation helpers (`utils/validation.py`), response helpers (`utils/responses.py`), and repository logic (`storage_db.py`).
- Applied the Repository pattern to `storage_db.py`, reducing duplication across CRUD operations and enforcing single responsibility.
- Added type hints and docstrings throughout the service layer to improve IDE/tooling support.

### 2.3 SOLID Principles & Error Handling
- **Single Responsibility / Open-Closed**: expense, category, budget, and auth concerns were separated into smaller functions and classes that can evolve independently.
- **Dependency Inversion**: routes now depend on repository abstractions rather than raw SQLAlchemy calls.
- **Improved Validation**: central validation helpers catch negative amounts, invalid dates, and missing required fields before hitting the database, reducing defensive code in routes.
- **Consistent Responses**: JSON payloads and HTTP status codes are standardized via the response helpers.

### 2.4 Outcomes
- Code review friction dropped significantly because diffs are localized.
- New team members can understand the data flow (controllers → services → repositories) quickly.
- Configuration mistakes are easier to spot because secrets and defaults are documented in `ENVIRONMENT.md`.

---

## 3. Testing and Coverage

### 3.1 Test Suite Expansion
- Added focused unit tests for utilities, validators, and repositories.
- Created integration tests that exercise the entire signup → add expense → dashboard workflow using Flask’s test client and an ephemeral SQLite DB.
- Added regression tests for budgets and categories to ensure future refactors respect business logic.

### 3.2 Coverage Enforcement
- Coverage consistently sits at **98 %** for backend modules (`app.py`, `storage_db.py`, `db.py`, etc.).
- `pytest --cov=. --cov-report=html --cov-report=term --cov-fail-under=70` runs locally and in CI; failing the gate blocks merges and deployments.
- HTML coverage reports are uploaded as GitHub Actions artifacts for manual inspection.

### 3.3 Developer Experience
- `pytest.ini` configures test discovery, warnings filters, and Ruff lint integration so contributors can run `pytest` without flags.
- `.coveragerc` (referenced in the tests) keeps noise low by omitting virtual environments and `__pycache__`.
- Test data factories/fixtures make it easy to add new cases with minimal boilerplate.

---

## 4. Continuous Integration (CI) Pipeline

### 4.1 Workflow Overview
- Workflow file: `.github/workflows/ci.yml`.
- Triggered on every push, pull request, and manual dispatch.
- Job matrix for Python 3.9, 3.10, and 3.11 to guarantee compatibility.

### 4.2 Steps
1. **Install dependencies** – uses pip cache to keep runs < 3 minutes.
2. **Static analysis** – Ruff linting covers style + simple bug patterns.
3. **Tests & coverage** – pyro-run with coverage enforcement.
4. **Build sanity check** – ensures critical modules can be imported and configuration files load without missing env vars.

### 4.3 Reporting
- Status badge embedded near the top of `README.md`.
- Coverage artifacts are downloadable from the Actions tab.
- Fail-fast is disabled so all Python versions report results even if one fails.

### 4.4 Impact
- Prevents regressions from landing on `main` because every PR/commit must pass tests and meet coverage.
- Gives Render deployment confidence (Branch 5.4) because CD only triggers after CI succeeds.

---

## 5. Deployment & Containerization

### 5.1 Dockerization
- Multi-stage Dockerfile: builder stage installs dependencies system-wide (no `--user`), runtime stage copies only what’s needed, minimizing image size and attack surface.
- Created `.dockerignore` to exclude venvs, tests, coverage artifacts, and macOS metadata (`.DS_Store`).
- Added `docker-compose.yml` for local dev plus `docker-compose.monitoring.yml` for observability tooling.
- Non-root user (`appuser`) runs the Flask process; container exposes port 5001 and reads env vars at runtime.

### 5.2 Render Deployment (Branch 5)
- Render Docker Web Service connected to the GitHub repo with auto-deploy on `main`.
- Environment variables (`FLASK_SECRET_KEY`, `DATABASE_URL`, `PORT`, `FLASK_DEBUG=0`, `PGSSLMODE=require`) configured via Render dashboard.
- Originally attempted persistent SQLite disk; migrated to **Render PostgreSQL** for durability and free-tier compatibility.
- Added `psycopg2-binary` dependency and made SQL queries dialect-aware (`strftime` vs `to_char`) to support both SQLite (local/tests) and Postgres (production).
- Health checks wired to `/api/health`, eliminating cold-start loops seen when Flask ran in debug mode.

### 5.3 Continuous Deployment
- `.github/workflows/cd-render.yml` POSTs to a Render Deploy Hook when `main` updates and CI passes.
- Hook URL stored as GitHub Secret `RENDER_DEPLOY_HOOK`; workflow logs include HTTP status for traceability.
- Manual redeploys / rollbacks documented in README (Render “Events” tab).

### 5.4 Verification Evidence
- Screenshots placed in `docs/screenshots/render-verification/`, covering:
  - Sign up / sign in / sign out flows
  - Expense CRUD + chart refresh
  - Monthly budget status display
  - Category add/delete and dropdown sync
  - `/api/health` and `/metrics` responses
  - Post-CD redeploy persistence check (data survives rerun of `cd-render`)
- Implementation Plan Branch 5.6 updated with timestamps and screenshot names to satisfy audit requirements.

---

## 6. Monitoring and Operational Readiness

### 6.1 Health Endpoint
- `/api/health` now reports:
  - `status` (`healthy`, `degraded`, `unhealthy`)
  - `db` connection result
  - `uptime_seconds`
  - `git_sha`
  - Timestamp (ISO 8601)
- Render and Azure prototypes both use this path for platform-level health checks.

### 6.2 Metrics Endpoint
- `/metrics` exposes Prometheus-formatted counters/histograms using `prometheus-client`.
- Captures request totals, latency buckets (p50/p95/p99 in Grafana), error counts, and active user gauges.
- Safe for unauthenticated GETs; no PII is emitted.

### 6.3 Prometheus + Grafana Stack
- `prometheus.yml` scrapes the Flask container every 15 seconds.
- `grafana/dashboards/expense-tracker.json` visualizes:
  - Request rate per route
  - Error rate
  - Response-time percentiles
  - Active sessions / sign-in spikes
- `docker-compose.monitoring.yml` spins up:
  - `prometheus` service bound to port 9090
  - `grafana` service on port 3000 with provisioned dashboard and datasource
- Developers can run `docker compose -f docker-compose.monitoring.yml up` to replicate the monitoring stack locally.

### 6.4 Alerting & Future Enhancements
- Current scope stops at dashboards; alerts can be added by extending `prometheus_alerts.yml` (scaffolded but optional).
- Grafana supports Slack/email integrations if credentials are added later.

---

## 7. Documentation & Knowledge Sharing

- `README.md` now covers quick start, Docker, Render deployment, environment variables, CI/CD, monitoring, troubleshooting, and verification checklist.
- `ENVIRONMENT.md` itemizes every env var, default, and location (local, GitHub, Render) to prevent misconfiguration.
- `IMPLEMENTATION_PLAN.md` tracks progress through all branches, including pivot history (Azure prototype) and verification evidence.
- This `REPORT.md` satisfies the requirement for a 5–6 page narrative summarizing the DevOps improvements.
- Screenshots + notes provide non-code evidence of deployment health, useful for demonstrations or audits.

---

## 8. Conclusion & Next Steps

The Expense Tracker project evolved from a monolithic Flask demo into a production-ready service with disciplined DevOps practices:

- Clean architecture and SOLID refactors make the codebase easier to extend (e.g., future mobile clients, currency features).
- Automated tests with near-100 % coverage and GitHub Actions enforce quality on every commit.
- Docker + Render deployment provides a reproducible runtime, while Postgres ensures persistent data without manual disks.
- Health checks, metrics, and Grafana dashboards enable proactive monitoring instead of reactive debugging.
- Documentation (README, ENVIRONMENT, IMPLEMENTATION_PLAN, REPORT) enables classmates, instructors, or future contributors to reproduce the entire setup.

**Future opportunities**:
- Add automated Playwright/Cypress smoke tests to the pipeline.
- Wire Prometheus alerts to email/Slack for error spikes or slow requests.
- Introduce Infrastructure-as-Code (e.g., Terraform for Render resources) for full reproducibility.
- Expand CD to blue/green deployments or Render Preview Environments for pull requests.

With these foundations in place, the application is stable, observable, and easily deployable—meeting the assignment’s objectives and providing a platform for future enhancements.

