# LUKHAS AI Gunicorn Configuration
# Production WSGI server configuration for LUKHAS AI system

import multiprocessing
import os

import psutil

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "lukhas-ai"

# User and group
user = None  # Will use the container user
group = None

# Paths
tmp_upload_dir = "/tmp"

# Logging
accesslog = "/app/logs/gunicorn-access.log"
errorlog = "/app/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process management
pidfile = "/app/lukhas-ai.pid"
daemon = False

# SSL (if using HTTPS directly)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment
raw_env = [
    "LUKHAS_GUNICORN=true",
]


# Hooks for Constellation Framework integration
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 LUKHAS AI starting up - Constellation Framework initializing")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 LUKHAS AI reloading - Constellation Framework reconnecting")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ LUKHAS AI ready - Constellation Framework: ⚛️🧠🛡️ online")
    server.log.info(f"👥 Workers: {workers} | 🔗 Connections per worker: {worker_connections}")


def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"⚠️  Worker {worker.pid} interrupted - graceful shutdown initiated")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"🔄 Forking worker {worker.age}")


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"✨ Worker {worker.pid} spawned (age: {worker.age})")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"🧠 Worker {worker.pid} initialized - LUKHAS consciousness active")


def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.error(f"💥 Worker {worker.pid} aborted")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 LUKHAS AI master process restarting")


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    # Log high-level request info for Constellation Framework monitoring
    worker.log.debug(f"🔍 Processing: {req.method} {req.path}")


def post_request(worker, req, _environ, resp):
    """Called after a worker processes the request."""
    # Enhanced logging for Constellation Framework analytics
    worker.log.debug(f"✅ Completed: {req.method} {req.path} -> {resp.status}")


# Custom application callable for LUKHAS AI
def application(environ, start_response):
    """
    WSGI application entry point for LUKHAS AI.
    This should be overridden by the actual application.
    """
    try:
        # Import the actual LUKHAS AI application
        from main import create_app

        app = create_app()
        return app(environ, start_response)
    except ImportError as e:
        # Fallback for testing
        response_body = f"LUKHAS AI Constellation Framework ⚛️🧠🛡️\nError: {e!s}\n"
        status = "500 Internal Server Error"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [response_body.encode()]


# Development vs Production settings
if os.getenv("LUKHAS_ENVIRONMENT") == "development":
    # Development overrides
    workers = 1
    reload = True
    loglevel = "debug"
    accesslog = "-"  # stdout
    errorlog = "-"  # stderr

elif os.getenv("LUKHAS_ENVIRONMENT") == "production":
    # Production optimizations
    preload_app = True
    max_requests = 2000
    max_requests_jitter = 100
    worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files

# Performance tuning based on available memory

memory_gb = psutil.virtual_memory().total / (1024**3)

if memory_gb >= 8:
    # High memory configuration
    workers = min(workers, 16)  # Cap at 16 workers
    worker_connections = 2000
elif memory_gb >= 4:
    # Medium memory configuration
    workers = min(workers, 8)
    worker_connections = 1500
else:
    # Low memory configuration
    workers = min(workers, 4)
    worker_connections = 1000
