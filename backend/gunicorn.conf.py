import os

from src.logger import LOGGING_CONFIG

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", 2))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))

# Logging — applied at Logger init, before the first gunicorn log line.
# Access log is handled by RequestAccessMiddleware.
accesslog = None
logconfig_dict = LOGGING_CONFIG


def on_starting(server):
    """Called in master process before workers are forked.

    Sets WORKERS_CONFIGURED so alerting rules can compare it against
    the live worker count without hardcoding the threshold.
    """
    from src.observability.prometheus.constants import WORKERS_CONFIGURED

    WORKERS_CONFIGURED.set(workers)


def post_fork(server, worker):
    """Called in worker process after fork.

    Sets WORKERS_GAUGE to 1 for this worker. Since the gauge uses
    multiprocess_mode='livesum', prometheus aggregates all live workers
    to produce the total active worker count.
    """
    from src.observability.prometheus.constants import WORKERS_GAUGE

    WORKERS_GAUGE.set(1)


def child_exit(server, worker):
    """Called in master process when a worker exits.

    Marks the worker's prometheus metrics files as dead so they are
    excluded from aggregation by MultiProcessCollector.
    """
    from prometheus_client import multiprocess as prom_mp

    prom_mp.mark_process_dead(worker.pid)
