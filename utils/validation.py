"""Validation helpers and decorators for request payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from flask import Request, request

from .responses import error_response


class ValidationError(ValueError):
    """Raised when a request payload fails validation."""


def require_json_body(*required_fields: str, error_message: Optional[str] = None):
    """Decorator that ensures a JSON body is present and optionally enforces required fields."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = _get_json_body(request)
            try:
                if required_fields:
                    _enforce_required_fields(data, required_fields, error_message)
            except ValidationError as exc:
                return error_response(str(exc), status=400)

            kwargs["json_data"] = data
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_json_body(req: Request) -> Dict[str, Any]:
    payload = req.get_json(force=True, silent=True)
    if not isinstance(payload, Mapping):
        return {}
    return dict(payload)


def _enforce_required_fields(
    payload: Mapping[str, Any],
    required_fields: Sequence[str],
    error_message: Optional[str],
) -> None:
    missing: List[str] = [
        field for field in required_fields if not _has_value(payload.get(field))
    ]
    if missing:
        msg = error_message or f"{', '.join(missing)} required"
        raise ValidationError(msg)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def validate_credentials(payload: Mapping[str, Any]) -> Tuple[str, str]:
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        raise ValidationError("username and password required")
    return username, password


def parse_positive_amount(value: Any, *, field: str = "amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid or missing '{field}' (must be number)")
    if amount <= 0:
        raise ValidationError(f"{field.capitalize()} must be greater than 0")
    return amount


def parse_optional_positive_amount(value: Any, *, field: str = "amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid '{field}'")
    if amount <= 0:
        raise ValidationError(f"{field.capitalize()} must be greater than 0")
    return amount


def parse_iso_date(value: Optional[str], *, default_to_today: bool = False) -> str:
    if not value:
        if default_to_today:
            return datetime.now(timezone.utc).date().isoformat()
        raise ValidationError("Invalid 'date' format. Use YYYY-MM-DD.")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError("Invalid 'date' format. Use YYYY-MM-DD.") from exc
    return value


def normalize_category(value: Optional[str]) -> str:
    return (value or "Uncategorized").strip() or "Uncategorized"


def normalize_note(value: Optional[str]) -> str:
    return (value or "").strip()


def build_expense_payload(user_id: int, payload: Mapping[str, Any]) -> Dict[str, Any]:
    amount = parse_positive_amount(payload.get("amount"))
    category = normalize_category(payload.get("category"))
    note = normalize_note(payload.get("note"))
    date_value = parse_iso_date(payload.get("date"), default_to_today=True)
    return {
        "user_id": user_id,
        "amount": amount,
        "category": category,
        "date": date_value,
        "note": note,
    }


def build_expense_update(payload: Mapping[str, Any]) -> Dict[str, Any]:
    updates: Dict[str, Any] = {}
    if "amount" in payload:
        updates["amount"] = parse_optional_positive_amount(payload.get("amount"))
    if "category" in payload:
        updates["category"] = normalize_category(payload.get("category"))
    if "date" in payload:
        updates["date"] = parse_iso_date(payload.get("date"), default_to_today=False)
    if "note" in payload:
        updates["note"] = normalize_note(payload.get("note"))
    if not updates:
        raise ValidationError("No valid update fields provided")
    return updates


def parse_month(value: Optional[str], *, default_to_current: bool = True) -> str:
    month = (value or "").strip()
    if not month and default_to_current:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
    if not month:
        raise ValidationError("Invalid 'month' format. Use YYYY-MM.")
    try:
        datetime.strptime(month + "-01", "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError("Invalid 'month' format. Use YYYY-MM.") from exc
    return month


def parse_budget_limit(value: Any) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Invalid or missing 'limit_amount' (must be number)")
    if amount <= 0:
        raise ValidationError("limit_amount must be greater than 0")
    return amount


def validate_category_name(value: Optional[str]) -> str:
    name = (value or "").strip()
    if not name:
        raise ValidationError("name required")
    return name


def filter_expenses_by_date_range(
    expenses: List[Dict[str, Any]], date_from: Optional[str], date_to: Optional[str]
) -> List[Dict[str, Any]]:
    """Filter expenses by date range, returning items within the specified range."""
    if not date_from and not date_to:
        return expenses

    def in_range(expense: Dict[str, Any]) -> bool:
        expense_date = expense.get("date")
        if not expense_date:
            return True
        if date_from and expense_date < date_from:
            return False
        if date_to and expense_date > date_to:
            return False
        return True

    return [exp for exp in expenses if in_range(exp)]


def filter_expenses_by_category(
    expenses: List[Dict[str, Any]], category: Optional[str]
) -> List[Dict[str, Any]]:
    """Filter expenses by category, returning items matching the category or all if category is None."""
    if category is None:
        return expenses
    return [exp for exp in expenses if exp.get("category") == category]


def sort_expenses_by_date_and_id(expenses: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """Sort expenses by date (descending) and then by id (descending)."""
    return sorted(expenses, key=lambda x: (x.get("date", ""), x.get("id", 0)), reverse=reverse)


def require_authenticated_user(get_user_fn: Callable[[], Optional[Dict[str, Any]]]):
    """Decorator factory that requires an authenticated user for route handlers."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_user_fn()
            if not user:
                return error_response("authentication required", status=401)
            kwargs["user"] = user
            return func(*args, **kwargs)
        return wrapper
    return decorator

