"""Utilities for building consistent JSON responses."""

from __future__ import annotations

from typing import Any, Mapping, Union

from flask import jsonify

JsonPayload = Union[Mapping[str, Any], list, str, int, float, None]


def json_response(payload: JsonPayload, status: int = 200):
    """Return a Flask JSON response tuple."""
    return jsonify(payload), status


def error_response(message: str, status: int = 400, **extra):
    """Return a standardized error response."""
    body = {"error": message}
    if extra:
        body.update(extra)
    return jsonify(body), status


