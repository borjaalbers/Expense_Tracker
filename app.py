# app.py
from typing import Any, Dict, Optional

from flask import Flask, Response, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
# Use SQLite database storage exclusively
from db import ENGINE
from models import Base
from services import AuthService, BudgetService, CategoryService, ExpenseService
import storage_db as storage  # Backwards compatibility for tests
from utils.responses import error_response, json_response
from utils.validation import (
    ValidationError,
    build_expense_payload,
    build_expense_update,
    filter_expenses_by_category,
    filter_expenses_by_date_range,
    parse_budget_limit,
    parse_month,
    require_json_body,
    sort_expenses_by_date_and_id,
    validate_category_name,
    validate_credentials,
)

Base.metadata.create_all(bind=ENGINE)

# Health check module
import health_check

# Metrics module
import metrics

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
# Secret key for sessions - in production use env var
app.secret_key = Config.SECRET_KEY

auth_service = AuthService(lambda: storage)
expense_service = ExpenseService(lambda: storage)
budget_service = BudgetService(lambda: storage)
category_service = CategoryService(lambda: storage)

# Initialize health check tracking and metrics collection
def _initialize_monitoring():
    """Initialize monitoring components safely."""
    try:
        health_check.initialize_health_check()
        metrics.track_request_metrics(app)
    except Exception:
        # Silently fail if monitoring can't be initialized (e.g., in some test environments)
        # Monitoring will still work if initialized later
        pass

# Initialize monitoring after app creation
_initialize_monitoring()

# --------------------------
# Helper utilities
# --------------------------
def current_user() -> Optional[Dict[str, Any]]:
    """Return the currently authenticated user or None."""
    uid = session.get("user_id")
    if not uid:
        return None
    return auth_service.get_user_by_id(uid)


def require_auth() -> Optional[tuple[Response, int]]:
    """Check if user is authenticated, return error response if not."""
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    return None


def require_login_json() -> Optional[tuple[Response, int]]:
    """Backward-compatible helper used in legacy tests (alias of require_auth)."""
    return require_auth()


def check_expense_ownership(expense: Optional[Dict[str, Any]], user_id: int) -> bool:
    """Verify that an expense exists and belongs to the specified user."""
    return expense is not None and expense.get("user_id") == user_id


def login_user(user: Dict[str, Any]) -> None:
    """Persist authenticated user identifiers in the session."""
    session["user_id"] = user["id"]
    session["username"] = user["username"]


def logout_user() -> None:
    """Clear authentication information from the session."""
    session.pop("user_id", None)
    session.pop("username", None)

# --------------------------
# Pages
# --------------------------
@app.route("/")
def index() -> Response:
    """Render the landing page or redirect authenticated users."""
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/dashboard")
def dashboard() -> Response:
    """Render the dashboard for authenticated users or redirect guests."""
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    return render_template("dashboard.html", username=user["username"])

# --------------------------
# Auth endpoints (JSON)
# --------------------------
@app.route("/api/signup", methods=["POST"])
@require_json_body("username", "password", error_message="username and password required")
def api_signup(json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Create a user from JSON credentials and establish a session."""
    try:
        username, password = validate_credentials(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    existing = auth_service.get_user_by_username(username)
    if existing:
        return error_response("username already exists", status=400, details="Choose a different username.")
    pw_hash = generate_password_hash(password)
    saved = auth_service.create_user(username, pw_hash)
    login_user(saved)
    payload = {"message": "created", "user": {"id": saved["id"], "username": saved["username"]}}
    return json_response(payload, status=201)

@app.route("/api/signin", methods=["POST"])
@require_json_body("username", "password", error_message="username and password required")
def api_signin(json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Authenticate existing users and start their session."""
    try:
        username, password = validate_credentials(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    user = auth_service.get_user_by_username(username)
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return error_response("invalid credentials", status=401, details="Username or password is incorrect.")
    login_user(user)
    payload = {"message": "signed in", "user": {"id": user["id"], "username": user["username"]}}
    return json_response(payload, status=200)

@app.route("/api/signout", methods=["POST"])
def api_signout() -> tuple[Response, int]:
    """Terminate the current session."""
    logout_user()
    return json_response({"message": "signed out"}, status=200)

# --------------------------
# Expense endpoints (JSON, per-user)
# --------------------------
@app.route("/api/expenses", methods=["POST"])
@require_json_body("amount", error_message="Invalid or missing 'amount' (must be number)")
def api_add_expense(json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Persist a new expense for the authenticated user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    try:
        expense = build_expense_payload(user["id"], json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    saved = expense_service.create_expense(expense)
    return json_response(saved, status=201)

@app.route("/api/expenses", methods=["GET"])
def api_list_expenses() -> tuple[Response, int]:
    """Return expenses for the authenticated user with optional filters."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    items = expense_service.list_user_expenses(user["id"])
    filtered = filter_expenses_by_date_range(items, date_from, date_to)
    filtered = filter_expenses_by_category(filtered, category)
    filtered = sort_expenses_by_date_and_id(filtered, reverse=True)
    return json_response(filtered, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def api_get_expense(expense_id: int) -> tuple[Response, int]:
    """Return a specific expense owned by the authenticated user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    expense = expense_service.get_expense(expense_id)
    if not check_expense_ownership(expense, user["id"]):
        return error_response("not found", status=404, details="Expense not found or not owned by the user.")
    return json_response(expense, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
@require_json_body()
def api_update_expense(expense_id: int, json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Update an expense with validated fields."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    expense = expense_service.get_expense(expense_id)
    if not check_expense_ownership(expense, user["id"]):
        return error_response("not found", status=404, details="Expense not found or not owned by the user.")
    try:
        updates = build_expense_update(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    updated = expense_service.update_expense(expense_id, updates)
    return json_response(updated, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id: int) -> tuple[Response, int]:
    """Delete an expense for the authenticated user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    expense = expense_service.get_expense(expense_id)
    if not check_expense_ownership(expense, user["id"]):
        return error_response("not found", status=404, details="Expense not found or not owned by the user.")
    ok = expense_service.delete_expense(expense_id)
    if not ok:
        return error_response("delete failed", status=500, details="Expense could not be removed.")
    return json_response({"deleted": expense_id}, status=200)

# --------------------------
# Statistics endpoints
# --------------------------
@app.route("/api/summary", methods=["GET"])
def api_summary() -> tuple[Response, int]:
    """Return spending totals grouped by category for the current user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    sums = expense_service.summary_by_category(user["id"])
    return json_response(sums, status=200)

@app.route("/api/monthly", methods=["GET"])
def api_monthly() -> tuple[Response, int]:
    """Return chronological monthly spending totals for the current user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    months = expense_service.monthly_totals(user["id"])
    sorted_months = dict(sorted(months.items()))
    return json_response(sorted_months, status=200)


# --------------------------
# Budget endpoints
# --------------------------
@app.route("/api/budget", methods=["GET"])
def api_get_budget() -> tuple[Response, int]:
    """Return budget status for the requested month."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    try:
        month = parse_month(request.args.get("month"), default_to_current=True)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    status = budget_service.get_budget_status(user["id"], month)
    return json_response(status, status=200)


@app.route("/api/budget", methods=["POST"])
@require_json_body()
def api_set_budget(json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Create or update a budget for the requested month."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    try:
        month = parse_month(json_data.get("month"), default_to_current=True)
        limit_val = parse_budget_limit(json_data.get("limit_amount"))
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    saved = budget_service.save_budget(user["id"], month, limit_val)
    status = budget_service.get_budget_status(user["id"], month)
    return json_response({"budget": saved, "status": status}, status=200)


# --------------------------
# Categories endpoints
# --------------------------
@app.route("/api/categories", methods=["GET"])
def api_list_categories() -> tuple[Response, int]:
    """Return the categories available to the current user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    cats = category_service.list_categories(user["id"])
    return json_response(cats, status=200)


@app.route("/api/categories", methods=["POST"])
@require_json_body("name", error_message="name required")
def api_add_category(json_data: Dict[str, Any]) -> tuple[Response, int]:
    """Create a new category for the current user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    try:
        name = validate_category_name(json_data.get("name"))
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    try:
        cat = category_service.add_category(user["id"], name)
    except ValueError as e:
        return error_response(str(e), status=400, details="Category names must be unique per user.")
    return json_response(cat, status=201)


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def api_delete_category(category_id: int) -> tuple[Response, int]:
    """Delete a category owned by the user."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    user = current_user()
    ok = category_service.delete_category(user["id"], category_id)
    if not ok:
        return error_response("not found", status=404, details="Category not found or not owned by the user.")
    return json_response({"deleted": category_id}, status=200)


# --------------------------
# Health
# --------------------------
@app.route("/api/health", methods=["GET"])
def health():
    """
    Enhanced health check endpoint.
    
    Returns comprehensive health status including:
    - Application status (healthy, degraded, unhealthy)
    - Database connectivity
    - Application version
    - Uptime information
    """
    health_data, http_status = health_check.get_health_status()
    return jsonify(health_data), http_status

# --------------------------
# Metrics
# --------------------------
@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    """
    Prometheus metrics endpoint.
    
    Exposes application metrics in Prometheus format for scraping.
    """
    return metrics.get_metrics_response()

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
