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
   - [ ] Review current test coverage
   - [ ] Add missing test cases for edge cases
   - [ ] Test all error paths
   - [ ] Test validation functions
   - [ ] Test utility functions

2. **Add Integration Tests**
   - [ ] Test full user workflows (signup → add expense → view dashboard)
   - [ ] Test database operations end-to-end
   - [ ] Test authentication flow
   - [ ] Test budget calculation logic
   - [ ] Test category management flow

3. **Coverage Analysis**
   - [ ] Run coverage report: `pytest --cov=. --cov-report=html --cov-report=term`
   - [ ] Identify gaps in coverage
   - [ ] Add tests to reach 70%+ coverage
   - [ ] Ensure all critical paths are covered

4. **Test Configuration**
   - [ ] Update `pytest.ini` with coverage settings
   - [ ] Add coverage threshold configuration
   - [ ] Set up test database fixtures properly
   - [ ] Add test data factories if needed

5. **Generate Coverage Report**
   - [ ] Add coverage report to repository
   - [ ] Document how to view coverage report
   - [ ] Add `.coveragerc` or `pyproject.toml` for coverage config

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
   - [ ] Create `.github/workflows/ci.yml`
   - [ ] Configure Python version matrix (3.9, 3.10, 3.11)
   - [ ] Set up job dependencies

2. **Test Job**
   - [ ] Install dependencies
   - [ ] Run linting (optional: add flake8/black)
   - [ ] Run unit tests
   - [ ] Run integration tests
   - [ ] Generate coverage report
   - [ ] Check coverage threshold (≥ 70%)
   - [ ] Upload coverage artifacts

3. **Build Job**
   - [ ] Verify application can be imported
   - [ ] Check all dependencies install correctly
   - [ ] Validate configuration

4. **Pipeline Configuration**
   - [ ] Set up triggers (push, pull_request)
   - [ ] Configure failure conditions
   - [ ] Add status badges to README
   - [ ] Set up coverage reporting (Codecov optional)

5. **Secrets Management**
   - [ ] Document required environment variables
   - [ ] Use GitHub Secrets for sensitive values
   - [ ] Add example `.env.example` file

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
   - [ ] Use Python 3.9+ base image
   - [ ] Set working directory
   - [ ] Copy requirements and install dependencies
   - [ ] Copy application code
   - [ ] Expose port 5001
   - [ ] Set up entrypoint
   - [ ] Use non-root user (security best practice)
   - [ ] Optimize layers for caching

2. **Create .dockerignore**
   - [ ] Exclude virtual environment
   - [ ] Exclude test files (unless needed)
   - [ ] Exclude database files
   - [ ] Exclude IDE files

3. **Create docker-compose.yml**
   - [ ] Define Flask app service
   - [ ] Set up volume mounts for development
   - [ ] Configure environment variables
   - [ ] Set up database volume persistence
   - [ ] Add healthcheck

4. **Docker Optimization**
   - [ ] Multi-stage build (if beneficial)
   - [ ] Minimize image size
   - [ ] Use specific Python version tags

5. **Documentation**
   - [ ] Add Docker build instructions
   - [ ] Add docker-compose usage instructions
   - [ ] Document environment variables

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
   - [ ] Evaluate options: Heroku, Railway, Render, Fly.io
   - [ ] Select platform (recommendation: Railway or Render for simplicity)
   - [ ] Create account and project

2. **Platform-Specific Configuration**
   - [ ] Create platform config file (e.g., `Procfile` for Heroku, `railway.json` for Railway)
   - [ ] Configure build command
   - [ ] Configure start command
   - [ ] Set up port configuration

3. **Environment Variables**
   - [ ] Document all required env vars
   - [ ] Set up secrets in platform dashboard
   - [ ] Configure DATABASE_URL (use platform DB or external)
   - [ ] Set FLASK_SECRET_KEY
   - [ ] Set PORT (usually auto-set by platform)

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

