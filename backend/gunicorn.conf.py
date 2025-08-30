# Gunicorn configuration file for Alex Design Django application
# Production-ready configuration with proper worker settings

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Timeout settings
timeout = 300  # Increased from 30 to 5 minutes for large file uploads
keepalive = 2
graceful_timeout = 300  # Increased from 30 to 5 minutes

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "alex-design-gunicorn"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
sendfile = True
reuse_port = True

# Environment
raw_env = [
    "DJANGO_ENV=production",
    "PRODUCTION=true",
]

# Pre-fork hooks
def on_starting(server):
    server.log.info("Starting Alex Design Gunicorn server")

def on_reload(server):
    server.log.info("Reloading Alex Design Gunicorn server")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_exit(server, worker):
    server.log.info("Worker exited (pid: %s)", worker.pid)

def child_exit(server, worker):
    server.log.info("Child exited (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def on_exit(server):
    server.log.info("Server is shutting down")
