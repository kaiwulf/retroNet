import multiprocessing
import os

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class - asyncio for async support
worker_class = "asyncio"

# Bind address
bind = "0.0.0.0:8000"

# Keep-alive timeout
keep_alive_timeout = 65

# Maximum requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Access log configuration
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Worker timeout
timeout = 120