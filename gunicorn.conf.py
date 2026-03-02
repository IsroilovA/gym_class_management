"""Gunicorn configuration for production."""

import multiprocessing
import os

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# Worker processes
default_workers = multiprocessing.cpu_count() * 2 + 1
# Keep auto workers bounded to reduce OOM risk in small containers.
max_workers = int(os.getenv("GUNICORN_MAX_WORKERS", "3"))
workers = int(os.getenv("GUNICORN_WORKERS", min(default_workers, max_workers)))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")
worker_tmp_dir = "/dev/shm"

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Process naming
proc_name = "django-app"
