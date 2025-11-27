"""
Health check module for monitoring application status.

Provides comprehensive health checks including database connectivity,
application version, and uptime tracking.
"""
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db import ENGINE

# Application version
__version__ = "1.0.0"

# Track application startup time for uptime calculation
_start_time: Optional[float] = None


def initialize_health_check() -> None:
    """Initialize health check tracking by recording startup time."""
    global _start_time
    if _start_time is None:
        _start_time = time.time()


def get_uptime_seconds() -> float:
    """Get application uptime in seconds."""
    if _start_time is None:
        return 0.0
    return time.time() - _start_time


def get_uptime_human() -> str:
    """Get application uptime in human-readable format."""
    uptime_seconds = get_uptime_seconds()
    if uptime_seconds == 0:
        return "0s"
    
    delta = timedelta(seconds=int(uptime_seconds))
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def check_database_connectivity() -> Dict[str, Any]:
    """
    Check database connectivity by executing a simple query.
    
    Returns:
        Dict with 'connected' (bool) and 'error' (optional str) keys
    """
    try:
        with ENGINE.connect() as connection:
            # Execute a simple query to verify connectivity
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            return {"connected": True, "error": None}
    except SQLAlchemyError as e:
        return {"connected": False, "error": str(e)}
    except Exception as e:
        return {"connected": False, "error": f"Unexpected error: {str(e)}"}


def get_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status of the application.
    
    Returns:
        Dict with status information including:
        - status: 'healthy', 'degraded', or 'unhealthy'
        - version: Application version
        - uptime_seconds: Uptime in seconds
        - uptime: Human-readable uptime
        - database: Database connectivity status
        - timestamp: Current timestamp
    """
    db_check = check_database_connectivity()
    
    # Determine overall status
    if db_check["connected"]:
        status = "healthy"
        http_status = 200
    else:
        # Database failure makes the service unhealthy
        status = "unhealthy"
        http_status = 503  # Service Unavailable
    
    return {
        "status": status,
        "version": __version__,
        "uptime_seconds": get_uptime_seconds(),
        "uptime": get_uptime_human(),
        "database": {
            "connected": db_check["connected"],
            "error": db_check.get("error")
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, http_status

