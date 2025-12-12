from prometheus_client import Counter, Gauge, Histogram

INFO = Gauge(
    name="fastapi_app_info",
    documentation="FastAPI application information.",
    labelnames=["version"],
)
REQUESTS = Counter(
    name="fastapi_http_requests_total",
    documentation="Total count of requests by method and path.",
    labelnames=["path", "method"],
)
REQUESTS_IN_PROGRESS = Gauge(
    name="fastapi_http_requests_in_progress",
    documentation="Gauge of requests by method and path currently being processed",
    labelnames=["path", "method"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    name="fastapi_http_request_duration_seconds",
    documentation="Histogram of requests processing time by path (in seconds)",
    labelnames=["path", "method"],
)
RESPONSES = Counter(
    name="fastapi_http_responses_total",
    documentation="Total count of responses by method, path and status codes.",
    labelnames=["path", "method", "status_code"],
)
EXCEPTIONS = Counter(
    name="fastapi_http_exceptions_total",
    documentation="Total count of exceptions raised by path and exception type",
    labelnames=["path", "method", "exception_type"],
)
WORKERS_GAUGE = Gauge(
    name="fastapi_server_gunicorn_workers",
    documentation="Number of active Gunicorn workers",
    multiprocess_mode="livesum",
)
WORKERS_CONFIGURED = Gauge(
    name="fastapi_server_gunicorn_workers_configured",
    documentation="Number of Gunicorn workers configured to run",
    multiprocess_mode="livesum",
)
