Assignment 2 Report - Expense Tracker

Assignment 2 Report - Expense Tracker	1
Course: Software Development and DevOps	1
Student: Borja Albers-Schönberg	1
Professor: Borja Serra Planelles	1
1. Introduction	2
2. Code Quality and Refactoring	2
2.1 Configuration Management	2
2.2 Service Layer Refactoring	2
2.3 SOLID Principles and Code Quality	3
3. Testing and Coverage	3
3.1 Test Structure	3
3.2 Test Isolation and CI Integration	4
4. CI/CD Pipeline	4
4.1 Continuous Integration (CI)	4
4.2 Continuous Delivery (CD)	4
5. Containerization	4
5.1 Docker Setup	4
5.2 Local and Production Environment	5
6. Deployment	5
6.1 Azure Deployment Attempt	5
6.2 Final Deployment on Render	5
7. Monitoring and Observability	6
7.1 Application Health	6
7.2 Metrics and Visualization	6
8. Conclusion	6




https://github.com/borjaalbers/Expense_Tracker 

Course: Software Development and DevOps
Student: Borja Albers-Schönberg
Professor: Borja Serra Planelles
1. Introduction

This project focused on designing, deploying, and monitoring a containerized Flask application using modern DevOps practices. The primary goal was to implement a full DevOps lifecycle, encompassing code quality improvements, automated testing, continuous integration and delivery, containerization, deployment, and monitoring. Iterative development was central to the workflow, allowing for continuous evaluation of multiple deployment strategies to ensure reliability, maintainability, and operational simplicity. The project utilizes Flask, Python 3.11, SQLAlchemy, SQLite for local testing, PostgreSQL for production, Docker, Docker Compose, GitHub Actions, Prometheus, and Grafana.
2. Code Quality and Refactoring

Prior to refactoring, the application relied heavily on a monolithic app.py file, which combined route definitions, validation logic, database operations, and configuration values. This design limited maintainability, testability, and scalability. To improve the architecture, a number of structural and functional changes were implemented.
2.1 Configuration Management

Configuration management was centralized in a new config.py module, which houses all environment-specific settings, including Flask secret keys, port configuration, and default expense categories. An environment-variable-first approach was adopted, with sensible defaults for local development, while production secrets are securely stored in Render or GitHub Secrets. This eliminated hardcoded values and magic numbers throughout the codebase, improving maintainability and security.
2.2 Service Layer Refactoring

The application structure was refactored to introduce a service layer, encapsulated in the services/ directory. This layer includes four core domain services: AuthService for authentication and user management, ExpenseService for expense-related business logic, BudgetService to manage budget calculations and status thresholds, and CategoryService for category management and default seeding. Each service depends on protocol-based interfaces defined in services/interfaces.py, enabling dependency inversion and allowing repositories to be mocked during testing. The repository pattern was applied in storage_db.py, with a generic BaseRepository for common CRUD operations and specialized repositories for users, expenses, budgets, and categories. This three-layer architecture; comprising controllers (routes), services, and repositories; ensures clear separation of concerns, supports independent testing, and allows the business logic to evolve without impacting route handlers or database access code.
2.3 SOLID Principles and Code Quality

Compliance to SOLID principles was imperative. Each module was given a single responsibility, and services can be extended without modification, in accordance with the Open/Closed Principle. Protocol-based interfaces ensure that Liskov Substitution is maintained, while interface segregation keeps repository abstractions focused on their specific domain. Dependency inversion is achieved by having services rely on protocol abstractions rather than concrete implementations, facilitating easier testing and future scalability.

Code quality improvements also included comprehensive type annotations and docstrings, elimination of dead code, standardization of error messages, and extraction of repeated logic into helper functions. These measures enhance readability and maintainability, ensuring that functions remain concise and focused.
3. Testing and Coverage

Testing was a critical component of the refactoring and automation effort. A comprehensive suite of 139 tests was implemented, spanning unit, integration, and database tests. These tests achieved a 100% pass rate, with overall coverage of 98.23%, significantly exceeding the minimum 70% requirement.
3.1 Test Structure

The test suite is structured to cover each layer of the application. Model tests validate SQLAlchemy schema constraints and relationships, ensuring correct enforcement of uniqueness, cascading deletes, and proper associations between users, expenses, budgets, and categories. Repository tests verify CRUD operations, budget aggregation, monthly totals, and error handling, confirming that the data access layer behaves as expected under normal and edge-case scenarios. Route tests simulate user interactions, including signup, authentication, expense management, and health checks, while integration tests validate end-to-end workflows such as user registration, expense creation, budget lifecycle, and category management. Database configuration tests ensure the correct creation of SQLAlchemy engines and session management.
3.2 Test Isolation and CI Integration

Test isolation was achieved through an in-memory SQLite database for each test case, preventing state pollution and ensuring reproducibility. Shared fixtures in conftest.py streamline setup and teardown, including Flask test clients and sample user data. Coverage enforcement is integrated into the CI pipeline, failing builds if coverage falls below 70%, and generating HTML reports for review. This comprehensive approach to testing not only ensures reliability but also strengthens confidence in the deployment pipeline and future feature additions.
4. CI/CD Pipeline

Continuous integration and continuous delivery were implemented using GitHub Actions.
4.1 Continuous Integration (CI)

The CI workflow is triggered on code pushes, pull requests, and manual dispatch, and executes tests across Python versions 3.9, 3.10, and 3.11 to ensure compatibility. The pipeline installs dependencies, performs static code analysis using Ruff, executes the test suite with coverage enforcement, and validates the build by importing key modules to ensure that the application can start without runtime errors. Failing early on test or import errors prevents broken code from reaching the deployment stage, reinforcing code reliability.
4.2 Continuous Delivery (CD)

The CD workflow is triggered upon successful merges to the main branch. It interacts with Render via a secure Deploy Hook, which builds a Docker image from the repository and deploys it automatically. Deployment logs are captured, and any errors result in workflow failure. Manual dispatch is also supported, providing flexibility for ad hoc deployments. By separating CI and CD responsibilities, the pipeline maintains clarity and ensures that only verified code is promoted to production.
5. Containerization
5.1 Docker Setup

The application was containerized using Docker, with a multi-stage Dockerfile based on Python 3.11-slim. Dependencies are installed in a builder stage, and only necessary files are copied into a runtime stage, reducing image size and attack surface. The Flask application runs as a non-root user (appuser) and includes a HEALTHCHECK directive pointing to /api/health.
5.2 Local and Production Environment

Local development uses Docker Compose for orchestrating the Flask service (with SQLite for local database persistence), while a separate Compose file supports the monitoring stack with Prometheus and Grafana. Production deployment on Render uses managed PostgreSQL for data durability. These containerization practices ensure consistency across development, testing, and production environments, and facilitate reproducible deployments.
6. Deployment
6.1 Azure Deployment Attempt

The deployment strategy began with Azure App Service due to its robust enterprise features, including Azure Container Registry (ACR) integration, managed service capabilities, and scalable infrastructure. Deployment to Azure involved building and pushing a Docker image to ACR, configuring environment variables, and creating a Web App with an App Service Plan. Health checks were configured to monitor service availability.

However, during deployment, persistent ImagePullFailure errors were encountered despite verifying credentials, image tags, and access policies. These failures were infrastructure-related rather than application-specific, highlighting the operational complexities of enterprise cloud platforms.
6.2 Final Deployment on Render

After careful evaluation and considering project deadlines, a pragmatic decision was made to pivot to Render, which offered a simpler, more reliable workflow for containerized applications.

The final deployment on Render leverages a Docker Web Service linked to the GitHub repository, enabling automatic builds and deployments upon code changes. PostgreSQL is used as a managed database service, and database queries were refactored to be dialect-aware, supporting SQLite for local development and PostgreSQL in production. Health checks were configured to ensure automatic restarts and service monitoring.

This pivot illustrates a key DevOps principle: balancing technical feasibility with operational efficiency. While the Azure deployment attempt remains documented, Render provides a stable, automated, and production-ready environment, demonstrating the importance of choosing a deployment platform that aligns with project goals and resource constraints.
7. Monitoring and Observability

Monitoring was introduced via a Docker Compose stack including Prometheus and Grafana.
7.1 Application Health

Application health is exposed through a dedicated health_check.py module, which returns the service status, database connectivity, uptime, and timestamp.

7.2 Metrics and Visualization

Metrics are collected via metrics.py, exposing HTTP request counts, response durations, error totals, and active user gauges in Prometheus format. Prometheus scrapes these metrics at 15-second intervals, while Grafana visualizes trends through dashboards that provide insights into performance, error rates, and usage patterns. This modular observability approach separates monitoring logic from application code, ensuring maintainability and testability.

8. Conclusion

The Expense Tracker project demonstrates a full DevOps lifecycle in action. Code refactoring and the introduction of a service layer enhanced maintainability and testability, while a comprehensive testing strategy ensured confidence in functionality. Automated CI/CD pipelines enforce quality and enable rapid, reliable deployment to Render. Containerization guarantees consistency across environments, and the Prometheus-Grafana monitoring stack provides actionable insights into application health and performance. Collectively, these improvements address all six critical assignment branches, providing a robust, production-ready, and observable application.
