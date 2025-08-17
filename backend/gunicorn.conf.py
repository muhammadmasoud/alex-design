# Gunicorn configuration file for production deployment - Optimized for Image Portfolio
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"  # Only bind to localhost, NGINX will handle external connections
backlog = 2048

# Worker processes optimized for file uploads and image processing
workers = max(2, min(multiprocessing.cpu_count(), 4))  # Cap at 4 workers for better memory management
worker_class = "sync"  # Sync workers are better for file uploads
worker_connections = 1000
timeout = 300  # Extended timeout for large image uploads and processing
keepalive = 2

# Memory and performance optimizations
worker_tmp_dir = "/dev/shm"  # Use memory for temporary files (faster)
preload_app = True          # Preload for better performance and memory sharing

# Restart workers to prevent memory leaks from image processing
max_requests = 200          # Lower limit due to image processing memory usage
max_requests_jitter = 20    # Add some randomness to worker restarts

# File upload optimizations
limit_request_line = 8192       # Increase for large file uploads
limit_request_fields = 100
limit_request_field_size = 16384

# Logging configuration
accesslog = "-"  # Log to stdout (systemd will handle)
errorlog = "-"   # Log to stderr (systemd will handle)
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'  # Include response time

# Process naming
proc_name = "alex-design-portfolio"

# Server mechanics
daemon = False
pidfile = "/tmp/alex-design-gunicorn.pid"
user = None
group = None

# Environment variables for production
raw_env = [
    'DJANGO_ENV=production',
    'PRODUCTION=true',
    'LIGHTSAIL=true',
]

# Performance tuning
worker_rlimit_nofile = 4096  # Increase file descriptor limit
preload_app = True

# Graceful shutdown
graceful_timeout = 60

# Security
forwarded_allow_ips = "127.0.0.1"  # Only trust NGINX

# SSL (for future HTTPS setup)
# keyfile = None
# certfile = None
