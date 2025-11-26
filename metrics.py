"""
Prometheus metrics collection module.

Provides Prometheus metrics for monitoring the Expense Tracker application,
including request counts, latency, errors, and active users.
"""
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import request, Response

# Request counter - tracks total HTTP requests by method and endpoint
HTTP_REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request latency histogram - tracks request duration
HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Error counter - tracks HTTP errors by status code
HTTP_ERROR_COUNT = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['method', 'endpoint', 'status_code']
)

# Active users gauge - tracks currently authenticated users (optional)
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of currently authenticated users'
)


def track_request_metrics(app):
    """
    Register Flask middleware to track request metrics.
    
    This function sets up before_request and after_request hooks
    to automatically collect metrics for all HTTP requests.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        """Record request start time for latency calculation."""
        request.start_time = time.time()

    @app.after_request
    def after_request(response: Response) -> Response:
        """Record request metrics after response is generated."""
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0.0

        # Get endpoint (route pattern) and method
        endpoint = request.endpoint or 'unknown'
        method = request.method
        
        # Get status code
        status_code = response.status_code
        status_class = f"{status_code // 100}xx"

        # Record request count
        HTTP_REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status_class
        ).inc()

        # Record request duration
        HTTP_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Record errors (4xx and 5xx status codes)
        if status_code >= 400:
            HTTP_ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()

        return response


def update_active_users_count(active_count: int) -> None:
    """
    Update the active users metric.
    
    This should be called periodically or when user sessions change.
    For simplicity, this can be updated based on session tracking.
    
    Args:
        active_count: Number of currently active/authenticated users
    """
    ACTIVE_USERS.set(active_count)


def get_metrics_response() -> Response:
    """
    Generate Prometheus metrics response.
    
    Returns:
        Flask Response object with metrics in Prometheus format
    """
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )

