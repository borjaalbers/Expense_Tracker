# Implementation Plan - DevOps Assignment 2

## Overview
This document outlines the step-by-step plan to complete all 8 branches for improving the Expense Tracker application with DevOps practices.

## Branch Workflow Strategy

### Phase 1: Foundation (Branches 1-2)
**Goal**: Improve code quality and ensure comprehensive testing

### Phase 2: Automation (Branches 3-4)
**Goal**: Set up CI/CD and containerization

### Phase 3: Deployment & Monitoring (Branches 5-6)
**Goal**: Deploy to cloud and add monitoring

### Phase 4: Documentation (Branch 7)
**Goal**: Document everything for reproducibility

---

## Detailed Branch Plans

### 🌿 Branch 1: `refactor-code-quality` (25% weight)

#### Objectives:
- Remove code smells (duplication, long methods, hardcoded values)
- Apply SOLID principles
- Improve code maintainability

#### Tasks:

1. **Extract Configuration**
   - [x] Create `config.py` for all configuration values
   - [x] Move hardcoded values: secret keys, port numbers, default categories
   - [x] Use environment variables with sensible defaults

2. **Refactor `app.py`**
   - [x] Extract validation logic into separate functions/classes
   - [x] Create request validation decorators/helpers
   - [x] Split long route handlers into smaller functions
   - [x] Extract date parsing/validation into utility functions
   - [x] Create response formatting helpers

3. **Refactor `storage_db.py`**
   - [x] Extract common query patterns
   - [x] Create base repository class following Repository pattern
   - [x] Reduce code duplication in CRUD operations

4. **Apply SOLID Principles**
   - [x] Single Responsibility: Separate concerns (auth, expenses, budgets, categories)
   - [x] Open/Closed: Use dependency injection where appropriate
   - [x] Liskov Substitution: Ensure interfaces are properly defined
   - [x] Interface Segregation: Create focused interfaces
   - [x] Dependency Inversion: Depend on abstractions

5. **Code Quality Improvements**
   - [x] Add type hints throughout
   - [x] Add docstrings to all functions/classes
   - [x] Remove any dead code
   - [x] Improve error messages
   - [x] Extract expense filtering logic to utility functions
   - [x] Create authentication helper to reduce duplication
   - [x] Extract expense ownership checking to utility function

#### Files to Create/Modify:
- `config.py` (new) ✓
- `app.py` (refactor) ✓
- `storage_db.py` (refactor) ✓
- `utils/validation.py` (new) ✓
- `utils/responses.py` (new) ✓

#### Success Criteria:
- No hardcoded values in business logic
- Functions are < 50 lines
- Code follows SOLID principles
- All functions have docstrings

---

### 🧪 Branch 2: `testing` (20% weight)

#### Objectives:
- Achieve 70%+ code coverage
- Add integration tests
- Generate coverage reports

#### Tasks:

1. **Enhance Unit Tests**
   - [x] Review current test coverage
   - [x] Add missing test cases for edge cases
   - [x] Test all error paths
   - [x] Test validation functions
   - [x] Test utility functions

2. **Add Integration Tests**
   - [x] Test full user workflows (signup → add expense → view dashboard)
   - [x] Test database operations end-to-end
   - [x] Test authentication flow
   - [x] Test budget calculation logic
   - [x] Test category management flow

3. **Coverage Analysis**
   - [x] Run coverage report: `pytest --cov=. --cov-report=html --cov-report=term`
   - [x] Identify gaps in coverage
   - [x] Add tests to reach 70%+ coverage
   - [x] Ensure all critical paths are covered

4. **Test Configuration**
   - [x] Update `pytest.ini` with coverage & lint settings (Ruff)
   - [x] Add coverage threshold configuration
   - [x] Set up test database fixtures properly
   - [x] Add test data factories if needed

5. **Generate Coverage Report**
   - [x] Add coverage report to repository
   - [x] Document how to view coverage report
   - [x] Add `.coveragerc` or `pyproject.toml` for coverage config

#### Files to Create/Modify:
- `tests/test_integration.py` (new)
- `tests/test_utils.py` (new)
- `tests/test_validation.py` (new)
- `pytest.ini` (update)
- `.coveragerc` (new)
- `tests/README.md` (update)

#### Success Criteria:
- Coverage ≥ 70% for all backend files
- All integration tests pass
- Coverage report generated and included
- Tests run in < 30 seconds

---

### 🔄 Branch 3: `ci-pipeline` (20% weight)

#### Objectives:
- Create CI pipeline (GitHub Actions)
- Run tests automatically
- Measure coverage
- Build application
- Fail if tests fail or coverage < 70%

#### Tasks:

1. **Set Up GitHub Actions**
   - [x] Create `.github/workflows/ci.yml`
   - [x] Configure Python version matrix (3.9, 3.10, 3.11)
   - [x] Set up job dependencies

2. **Test Job**
   - [x] Install dependencies
   - [x] Run linting (optional: add flake8/black)
   - [x] Run unit tests
   - [x] Run integration tests
   - [x] Generate coverage report
   - [x] Check coverage threshold (≥ 70%)
   - [x] Upload coverage artifacts

3. **Build Job**
   - [x] Verify application can be imported
   - [x] Check all dependencies install correctly
   - [x] Validate configuration

4. **Pipeline Configuration**
   - [x] Set up triggers (push, pull_request, workflow_dispatch)
   - [x] Configure failure conditions (matrix fail-fast disabled, coverage gate)
   - [x] Add status badges to README
   - [x] Set up coverage reporting (HTML artifact via Actions)

5. **Secrets Management**
   - [x] Document required environment variables
   - [x] Use GitHub Secrets for sensitive values
   - [x] Add example `.env.example` file

#### Files to Create:
- `.github/workflows/ci.yml` (new)
- `.env.example` (new)
- `.gitignore` (update if needed)

#### Success Criteria:
- Pipeline runs on every push/PR
- Tests must pass for pipeline to succeed
- Coverage check fails if < 70%
- Build succeeds if all checks pass
- Pipeline completes in < 5 minutes

---

### 🐳 Branch 4: `dockerization` (Part of 20% weight)

#### Objectives:
- Containerize the application
- Create Dockerfile
- Set up docker-compose for local development

#### Tasks:

1. **Create Dockerfile**
   - [x] Use Python 3.9+ base image
   - [x] Set working directory
   - [x] Copy requirements and install dependencies
   - [x] Copy application code
   - [x] Expose port 5001
   - [x] Set up entrypoint
   - [x] Use non-root user (security best practice)
   - [x] Optimize layers for caching

2. **Create .dockerignore**
   - [x] Exclude virtual environment
   - [x] Exclude test files (unless needed)
   - [x] Exclude database files
   - [x] Exclude IDE files

3. **Create docker-compose.yml**
   - [x] Define Flask app service
   - [x] Set up volume mounts for development
   - [x] Configure environment variables
   - [x] Set up database volume persistence
   - [x] Add healthcheck

4. **Docker Optimization**
   - [x] Multi-stage build (if beneficial)
   - [x] Minimize image size
   - [x] Use specific Python version tags

5. **Documentation**
   - [x] Add Docker build instructions
   - [x] Add docker-compose usage instructions
   - [x] Document environment variables

#### Files to Create:
- `Dockerfile` (new)
- `.dockerignore` (new)
- `docker-compose.yml` (new)

#### Success Criteria:
- Docker image builds successfully
- Application runs in container
- Database persists correctly
- docker-compose works for local dev
- Image size < 500MB

---

### 🚀 Branch 5: `deployment` (Part of 20% weight)

#### Objectives:
- Deploy to cloud platform
- Configure secrets management
- Auto-deploy only from main branch

#### Tasks:

1. **Choose Deployment Platform**
   - [x] Evaluate options: Heroku, Railway, Render, Fly.io
   - [x] Select platform (Render chosen for Docker-native deploy + generous free tier)
   - [x] Create account and project

   **Evaluation Snapshot**

   | Platform | Pros | Cons | Fit |
   |----------|------|------|-----|
   | **Heroku** | Mature platform, Procfile support, add-ons marketplace | Free tier discontinued, container deploy requires paid dyno, cold starts on eco plan | ❌ Costs + no native Docker on free tier |
   | **Railway** | Simple UI, template-based deploys, Postgres add-on | Free tier credits reset monthly, projects sleep after inactivity, Docker deploy beta | ⚠️ OK but credits reset mid-review |
   | **Render** | First-class Docker support, free tier without credit reset, persistent disks, auto SSL, deploy-on-push | Free instances sleep after 15 min idle, Postgres limited to 1 GB on free tier | ✅ Best balance for assignment |
   | **Fly.io** | Global regions, private networking, CLI driven | Requires CLI + credit card verification, more ops overhead | ⚠️ Overkill for class project |

   Render wins because it deploys the existing Dockerfile with no code changes, supports GitHub auto-deployments from `main`, and keeps secrets + persistent storage in one dashboard.

   **Render Setup Checklist (completed)**
   1. Sign up with GitHub and authorize access to `borjaalbers/Expense_Tracker`.
   2. Create a **Web Service** named `expense-tracker` targeting branch `main`, region **Frankfurt**, runtime **Docker**, instance type **Free (0.1 CPU/512 MB)**.
   3. Seed env vars: `FLASK_SECRET_KEY=<generated>`, `DATABASE_URL=sqlite:////data/expense_tracker.db`, `PORT=5001`.
   4. Deploy latest commit (5d4dabc) and verify:
      - Root URL renders (sign up/in works, expenses can be added).
      - `/api/health` returns `{"status": "ok", ...}`.
      - Render logs show 200 responses and no runtime errors.

2. **Platform-Specific Configuration**
   - [x] Create platform config file (`render.yaml` blueprint for Render)
   - [x] Configure build command (Dockerfile referenced via blueprint)
   - [x] Configure start command (Docker `CMD ["python", "app.py"]`)
   - [x] Set up port configuration (`PORT=5001`, health check `/api/health`)

   **Render Blueprint Highlights**
   - `render.yaml` pins service name, region, plan, branch, Docker context, and health check path.
   - Environment variables defined with defaults plus a secret-only `FLASK_SECRET_KEY`.
   - Auto-deploy enabled for `main`; health check ensures container readiness.

3. **Environment Variables**
   - [x] Document all required env vars (`ENVIRONMENT.md` + README section)
   - [x] Set up secrets in platform dashboard (Render env vars + FLASK_DEBUG=0)
   - [x] Configure DATABASE_URL (SQLite default + notes for Render Postgres)
   - [x] Set FLASK_SECRET_KEY (documented generation steps)
   - [x] Set PORT (5001 locally/Render)

   **Highlights**
   - `.env.example` + new `ENVIRONMENT.md` describe every variable, defaults, and rotation guidance.
   - README links to the env guide; Render instructions ensure `FLASK_SECRET_KEY`, `DATABASE_URL`, `PORT`, and `FLASK_DEBUG` are set.

4. **Auto-Deployment Setup**
   - [ ] Connect GitHub repository
   - [ ] Configure to deploy only from `main` branch
   - [ ] Set up deployment triggers
   - [ ] Add deployment status badge

5. **Database Setup**
   - [ ] Use platform database service OR
   - [ ] Configure external database (e.g., PostgreSQL)
   - [ ] Update DATABASE_URL
   - [ ] Test database migrations

6. **Post-Deployment Verification**
   - [ ] Verify application is accessible
   - [ ] Test all endpoints
   - [ ] Verify database connectivity
   - [ ] Test authentication flow

#### Files to Create/Modify:
- `Procfile` or platform-specific config (new)
- `runtime.txt` (if needed for Python version)
- `README.md` (add deployment section)

#### Success Criteria:
- Application deployed and accessible
- Only main branch triggers deployment
- Secrets properly configured
- Database working correctly
- All endpoints functional

---

### 📊 Branch 6: `monitoring-health` (Part of 15% weight)

#### Objectives:
- Enhance `/health` endpoint
- Add metrics (request count, latency, errors)
- Set up Prometheus/Grafana configuration

#### Tasks:

1. **Enhance Health Endpoint**
   - [ ] Add database connectivity check
   - [ ] Add application version info
   - [ ] Return detailed status (healthy, degraded, unhealthy)
   - [ ] Add uptime information

2. **Add Metrics Collection**
   - [ ] Install `prometheus-client` library
   - [ ] Create metrics module
   - [ ] Add request count metric
   - [ ] Add request latency metric
   - [ ] Add error count metric
   - [ ] Add active users metric (optional)

3. **Expose Metrics Endpoint**
   - [ ] Create `/metrics` endpoint for Prometheus
   - [ ] Format metrics in Prometheus format
   - [ ] Test metrics collection

4. **Prometheus Configuration**
   - [ ] Create `prometheus.yml` configuration
   - [ ] Configure scrape interval
   - [ ] Set up target (application)
   - [ ] Add alerting rules (optional)

5. **Grafana Configuration**
   - [ ] Create `grafana/dashboards/expense-tracker.json`
   - [ ] Set up dashboard with key metrics:
     - Request rate
     - Error rate
     - Response time (p50, p95, p99)
     - Active users
   - [ ] Add screenshots or export dashboard config

6. **Docker Compose for Monitoring** (Optional)
   - [ ] Add Prometheus service to docker-compose
   - [ ] Add Grafana service to docker-compose
   - [ ] Configure networking between services

#### Files to Create:
- `metrics.py` (new)
- `prometheus.yml` (new)
- `grafana/dashboards/expense-tracker.json` (new)
- `docker-compose.monitoring.yml` (optional, new)
- `app.py` (modify to add metrics)

#### Success Criteria:
- `/health` endpoint returns detailed status
- `/metrics` endpoint exposes Prometheus metrics
- Prometheus can scrape metrics
- Grafana dashboard shows key metrics
- Metrics update in real-time

---

### 📝 Branch 7: `docs-report` (Part of 15% weight)

#### Objectives:
- Update README.md with deployment instructions
- Create REPORT.md (5-6 pages) summarizing improvements

#### Tasks:

1. **Update README.md**
   - [ ] Add "Deployment" section
   - [ ] Add Docker deployment instructions
   - [ ] Add cloud platform deployment instructions
   - [ ] Add environment variables documentation
   - [ ] Add CI/CD pipeline information
   - [ ] Add monitoring setup instructions
   - [ ] Update "Running Tests" section with coverage info
   - [ ] Add troubleshooting section for deployment

2. **Create REPORT.md**
   - [ ] **Introduction** (1 page)
     - Project overview
     - Objectives of Assignment 2
     - Structure of the report
   
   - [ ] **Code Quality and Refactoring** (1 page)
     - Code smells identified and fixed
     - SOLID principles applied
     - Refactoring examples (before/after)
     - Configuration management improvements
   
   - [ ] **Testing and Coverage** (1 page)
     - Test strategy
     - Coverage analysis
     - Integration tests added
     - Coverage report results
   
   - [ ] **CI/CD Pipeline** (1 page)
     - Pipeline architecture
     - Jobs and stages
     - Coverage enforcement
     - Build process
   
   - [ ] **Deployment and Containerization** (1 page)
     - Docker setup
     - Cloud deployment platform
     - Secrets management
     - Auto-deployment configuration
   
   - [ ] **Monitoring and Health Checks** (1 page)
     - Health endpoint enhancements
     - Metrics collection
     - Prometheus/Grafana setup
     - Dashboard screenshots or configs
   
   - [ ] **Conclusion** (0.5 pages)
     - Summary of improvements
     - Lessons learned
     - Future enhancements

3. **Additional Documentation**
   - [ ] Add architecture diagram (optional)
   - [ ] Add deployment diagram (optional)
   - [ ] Document all environment variables
   - [ ] Add troubleshooting guide

#### Files to Create/Modify:
- `REPORT.md` (new, 5-6 pages)
- `README.md` (update)
- `DEPLOYMENT.md` (optional, new)

#### Success Criteria:
- README.md is comprehensive and clear
- REPORT.md is 5-6 pages, well-structured
- All deployment steps documented
- Repository is runnable by others following docs

---

## Execution Order

### Recommended Sequence:

1. **Start with Branch 1** (`refactor-code-quality`)
   - Foundation for everything else
   - Makes testing easier

2. **Then Branch 2** (`testing`)
   - Build on refactored code
   - Establish coverage baseline

3. **Branch 3** (`ci-pipeline`)
   - Automate testing
   - Catch issues early

4. **Branch 4** (`dockerization`)
   - Containerize before deployment
   - Test locally first

5. **Branch 5** (`deployment`)
   - Deploy containerized app
   - Test in production-like environment

6. **Branch 6** (`monitoring-health`)
   - Monitor deployed application
   - Collect real metrics

7. **Branch 7** (`docs-report`)
   - Document everything
   - Write final report

8. **Final Merge**
   - Merge all branches to main
   - Final verification
   - Ensure everything works together

---

## Quick Reference Commands

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_app.py
```

### Docker
```bash
# Build image
docker build -t expense-tracker .

# Run container
docker run -p 5001:5001 expense-tracker

# Use docker-compose
docker-compose up
```

### CI/CD
```bash
# Test CI locally (using act or GitHub CLI)
gh workflow run ci.yml

# Check workflow status
gh run list
```

### Deployment
```bash
# Platform-specific commands will be documented in README
```

---

## Success Checklist

- [ ] All 7 branches completed
- [ ] Code coverage ≥ 70%
- [ ] CI pipeline passes
- [ ] Docker image builds and runs
- [ ] Application deployed to cloud
- [ ] Monitoring set up and working
- [ ] README.md updated
- [ ] REPORT.md created (5-6 pages)
- [ ] Repository is runnable by others
- [ ] All commits have meaningful messages
- [ ] Main branch only triggers deployment

---

## Notes

- Use meaningful commit messages for all changes
- Keep explanations concise and relevant
- Templates from class examples may be reused/adapted
- Test each branch thoroughly before moving to next
- Merge branches incrementally to catch integration issues early

---

## Timeline Estimate

- Branch 1: 2-3 hours
- Branch 2: 2-3 hours
- Branch 3: 1-2 hours
- Branch 4: 1-2 hours
- Branch 5: 1-2 hours
- Branch 6: 2-3 hours
- Branch 7: 2-3 hours
- Final merge & verification: 1 hour

**Total: ~12-18 hours**

---

*Last Updated: [Current Date]*

