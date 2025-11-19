# app.py
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Use SQLite database storage exclusively
from db import ENGINE
from models import Base

Base.metadata.create_all(bind=ENGINE)

from config import Config
from services import AuthService, BudgetService, CategoryService, ExpenseService
import storage_db as storage  # Backwards compatibility for tests
from utils.responses import error_response, json_response
from utils.validation import (
    ValidationError,
    build_expense_payload,
    build_expense_update,
    parse_budget_limit,
    parse_month,
    require_json_body,
    validate_category_name,
    validate_credentials,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
# Secret key for sessions - in production use env var
app.secret_key = Config.SECRET_KEY

auth_service = AuthService(lambda: storage)
expense_service = ExpenseService(lambda: storage)
budget_service = BudgetService(lambda: storage)
category_service = CategoryService(lambda: storage)

# --------------------------
# Helper utilities
# --------------------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return auth_service.get_user_by_id(uid)

def login_user(user):
    session["user_id"] = user["id"]
    session["username"] = user["username"]

def logout_user():
    session.pop("user_id", None)
    session.pop("username", None)

# --------------------------
# Pages
# --------------------------
@app.route("/")
def index():
    # If logged in, redirect to dashboard
    if current_user():
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    return render_template("dashboard.html", username=user["username"])

# --------------------------
# Auth endpoints (JSON)
# --------------------------
@app.route("/api/signup", methods=["POST"])
@require_json_body("username", "password", error_message="username and password required")
def api_signup(json_data):
    try:
        username, password = validate_credentials(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    existing = auth_service.get_user_by_username(username)
    if existing:
        return error_response("username already exists", status=400)
    pw_hash = generate_password_hash(password)
    saved = auth_service.create_user(username, pw_hash)
    login_user(saved)
    payload = {"message": "created", "user": {"id": saved["id"], "username": saved["username"]}}
    return json_response(payload, status=201)

@app.route("/api/signin", methods=["POST"])
@require_json_body("username", "password", error_message="username and password required")
def api_signin(json_data):
    try:
        username, password = validate_credentials(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    user = auth_service.get_user_by_username(username)
    if not user:
        return error_response("invalid credentials", status=401)
    if not check_password_hash(user.get("password_hash", ""), password):
        return error_response("invalid credentials", status=401)
    login_user(user)
    payload = {"message": "signed in", "user": {"id": user["id"], "username": user["username"]}}
    return json_response(payload, status=200)

@app.route("/api/signout", methods=["POST"])
def api_signout():
    logout_user()
    return json_response({"message": "signed out"}, status=200)

# --------------------------
# Expense endpoints (JSON, per-user)
# --------------------------
@app.route("/api/expenses", methods=["POST"])
@require_json_body("amount", error_message="Invalid or missing 'amount' (must be number)")
def api_add_expense(json_data):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    try:
        expense = build_expense_payload(user["id"], json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    saved = expense_service.create_expense(expense)
    return json_response(saved, status=201)

@app.route("/api/expenses", methods=["GET"])
def api_list_expenses():
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    # optional filters
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    items = expense_service.list_user_expenses(user["id"])
    def in_range(it):
        ds = it.get("date")
        if not ds:
            return True
        if date_from and ds < date_from:
            return False
        if date_to and ds > date_to:
            return False
        return True
    filtered = [it for it in items if (category is None or it.get("category") == category) and in_range(it)]
    filtered.sort(key=lambda x: (x.get("date",""), x.get("id", 0)), reverse=True)
    return json_response(filtered, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def api_get_expense(expense_id):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    expense = expense_service.get_expense(expense_id)
    if not expense or expense.get("user_id") != user["id"]:
        return error_response("not found", status=404)
    return json_response(expense, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
@require_json_body()
def api_update_expense(expense_id, json_data):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    it = expense_service.get_expense(expense_id)
    if not it or it.get("user_id") != user["id"]:
        return error_response("not found", status=404)
    try:
        updates = build_expense_update(json_data)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    updated = expense_service.update_expense(expense_id, updates)
    return json_response(updated, status=200)

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    it = expense_service.get_expense(expense_id)
    if not it or it.get("user_id") != user["id"]:
        return error_response("not found", status=404)
    ok = expense_service.delete_expense(expense_id)
    if not ok:
        return error_response("delete failed", status=500)
    return json_response({"deleted": expense_id}, status=200)

# --------------------------
# Statistics endpoints
# --------------------------
@app.route("/api/summary", methods=["GET"])
def api_summary():
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    sums = expense_service.summary_by_category(user["id"])
    return json_response(sums, status=200)

@app.route("/api/monthly", methods=["GET"])
def api_monthly():
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    months = expense_service.monthly_totals(user["id"])
    # sort months ascending
    sorted_months = dict(sorted(months.items()))
    return json_response(sorted_months, status=200)


# --------------------------
# Budget endpoints
# --------------------------
@app.route("/api/budget", methods=["GET"])
def api_get_budget():
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    try:
        month = parse_month(request.args.get("month"), default_to_current=True)
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    status = budget_service.get_budget_status(user["id"], month)
    return json_response(status, status=200)


@app.route("/api/budget", methods=["POST"])
@require_json_body()
def api_set_budget(json_data):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
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
def api_list_categories():
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    cats = category_service.list_categories(user["id"])
    return json_response(cats, status=200)


@app.route("/api/categories", methods=["POST"])
@require_json_body("name", error_message="name required")
def api_add_category(json_data):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    try:
        name = validate_category_name(json_data.get("name"))
    except ValidationError as exc:
        return error_response(str(exc), status=400)
    try:
        cat = category_service.add_category(user["id"], name)
    except ValueError as e:
        return error_response(str(e), status=400)
    return json_response(cat, status=201)


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def api_delete_category(category_id: int):
    user = current_user()
    if not user:
        return error_response("authentication required", status=401)
    ok = category_service.delete_category(user["id"], category_id)
    if not ok:
        return error_response("not found", status=404)
    return json_response({"deleted": category_id}, status=200)


# --------------------------
# Health
# --------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return json_response({"status": "ok", "user": session.get("username")}, status=200)

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
