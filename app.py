# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Use SQLite database storage exclusively
from db import ENGINE
from models import Base
Base.metadata.create_all(bind=ENGINE)
import storage_db as storage

app = Flask(__name__, template_folder="templates", static_folder="static")
# Secret key for sessions - in production use env var
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# --------------------------
# Helper utilities
# --------------------------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return storage.find_user_by_id(uid)

def login_user(user):
    session["user_id"] = user["id"]
    session["username"] = user["username"]

def logout_user():
    session.pop("user_id", None)
    session.pop("username", None)

def require_login_json():
    if not current_user():
        return jsonify({"error": "authentication required"}), 401
    return None

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
def api_signup():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if storage.find_user_by_username(username):
        return jsonify({"error": "username already exists"}), 400
    pw_hash = generate_password_hash(password)
    user = {"username": username, "password_hash": pw_hash}
    saved = storage.save_user(user)
    login_user(saved)
    return jsonify({"message": "created", "user": {"id": saved["id"], "username": saved["username"]}}), 201

@app.route("/api/signin", methods=["POST"])
def api_signin():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    user = storage.find_user_by_username(username)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    if not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"error": "invalid credentials"}), 401
    login_user(user)
    return jsonify({"message": "signed in", "user": {"id": user["id"], "username": user["username"]}}), 200

@app.route("/api/signout", methods=["POST"])
def api_signout():
    logout_user()
    return jsonify({"message": "signed out"}), 200

# --------------------------
# Expense endpoints (JSON, per-user)
# --------------------------
@app.route("/api/expenses", methods=["POST"])
def api_add_expense():
    # require login
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    data = request.get_json(force=True, silent=True) or {}
    try:
        amount = float(data.get("amount"))
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing 'amount' (must be number)"}), 400
    category = data.get("category", "Uncategorized")
    note = data.get("note", "")
    date_str = data.get("date")
    if date_str:
        try:
            datetime.fromisoformat(date_str)
        except Exception:
            return jsonify({"error": "Invalid 'date' format. Use YYYY-MM-DD."}), 400
    else:
        date_str = datetime.utcnow().date().isoformat()
    expense = {
        "user_id": user["id"],
        "amount": amount,
        "category": category,
        "date": date_str,
        "note": note
    }
    saved = storage.save_expense(expense)
    return jsonify(saved), 201

@app.route("/api/expenses", methods=["GET"])
def api_list_expenses():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    # optional filters
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    items = storage.get_user_expenses(user["id"])
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
    return jsonify(filtered), 200

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def api_get_expense(expense_id):
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    expense = storage.find_expense(expense_id)
    if not expense or expense.get("user_id") != user["id"]:
        return jsonify({"error": "not found"}), 404
    return jsonify(expense), 200

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def api_update_expense(expense_id):
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    it = storage.find_expense(expense_id)
    if not it or it.get("user_id") != user["id"]:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(force=True, silent=True) or {}
    allowed = {}
    if "amount" in data:
        try:
            amount = float(data["amount"])
            if amount <= 0:
                return jsonify({"error": "Amount must be greater than 0"}), 400
            allowed["amount"] = amount
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid 'amount'"}), 400
    if "category" in data:
        allowed["category"] = data["category"]
    if "date" in data:
        try:
            datetime.fromisoformat(data["date"])
            allowed["date"] = data["date"]
        except Exception:
            return jsonify({"error": "Invalid 'date' format. Use YYYY-MM-DD."}), 400
    if "note" in data:
        allowed["note"] = data["note"]
    if not allowed:
        return jsonify({"error": "No valid update fields provided"}), 400
    updated = storage.update_expense(expense_id, allowed)
    return jsonify(updated), 200

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    it = storage.find_expense(expense_id)
    if not it or it.get("user_id") != user["id"]:
        return jsonify({"error": "not found"}), 404
    ok = storage.delete_expense(expense_id)
    if not ok:
        return jsonify({"error": "delete failed"}), 500
    return jsonify({"deleted": expense_id}), 200

# --------------------------
# Statistics endpoints
# --------------------------
@app.route("/api/summary", methods=["GET"])
def api_summary():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    sums = storage.summary_by_category(user["id"])
    return jsonify(sums), 200

@app.route("/api/monthly", methods=["GET"])
def api_monthly():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    months = storage.monthly_totals(user["id"])
    # sort months ascending
    sorted_months = dict(sorted(months.items()))
    return jsonify(sorted_months), 200


# --------------------------
# Budget endpoints
# --------------------------
@app.route("/api/budget", methods=["GET"])
def api_get_budget():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    month = request.args.get("month")
    if not month:
        # default to current month in UTC
        month = datetime.utcnow().strftime("%Y-%m")
    # validate YYYY-MM
    try:
        datetime.strptime(month + "-01", "%Y-%m-%d")
    except Exception:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM."}), 400
    status = storage.get_budget_status(user["id"], month)
    return jsonify(status), 200


@app.route("/api/budget", methods=["POST"])
def api_set_budget():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    data = request.get_json(force=True, silent=True) or {}
    month = (data.get("month") or "").strip()
    limit_amount = data.get("limit_amount")
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")
    try:
        datetime.strptime(month + "-01", "%Y-%m-%d")
    except Exception:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM."}), 400
    try:
        limit_val = float(limit_amount)
        if limit_val <= 0:
            return jsonify({"error": "limit_amount must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing 'limit_amount' (must be number)"}), 400
    saved = storage.upsert_budget(user["id"], month, limit_val)
    status = storage.get_budget_status(user["id"], month)
    return jsonify({"budget": saved, "status": status}), 200


# --------------------------
# Categories endpoints
# --------------------------
@app.route("/api/categories", methods=["GET"])
def api_list_categories():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    cats = storage.list_categories(user["id"])
    return jsonify(cats), 200


@app.route("/api/categories", methods=["POST"])
def api_add_category():
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    try:
        cat = storage.add_category(user["id"], name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(cat), 201


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def api_delete_category(category_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "authentication required"}), 401
    ok = storage.delete_category(user["id"], category_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": category_id}), 200


# --------------------------
# Health
# --------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "user": session.get("username")}), 200

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=True)
