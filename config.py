"""Centralized configuration for the Expense Tracker application."""

from __future__ import annotations

import os
from typing import List


def _env_bool(var_name: str, default: bool) -> bool:
    val = os.environ.get(var_name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


def _env_list(var_name: str, fallback: List[str], separator: str = ",") -> List[str]:
    raw = os.environ.get(var_name)
    if not raw:
        return fallback
    parsed = [item.strip() for item in raw.split(separator)]
    return [item for item in parsed if item]


_DEFAULT_CATEGORY_FALLBACK = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Groceries",
    "Other",
]


class Config:
    """Application configuration with sensible defaults."""

    SECRET_KEY: str = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    HOST: str = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", "5001")))
    DEBUG: bool = _env_bool("FLASK_DEBUG", True)
    DEFAULT_CATEGORIES: List[str] = _env_list("DEFAULT_CATEGORIES", _DEFAULT_CATEGORY_FALLBACK)


