# Gunicorn config
bind = "0.0.0.0:8000"
workers = 2
threads = 4
worker_class = "gthread"
timeout = 120
keepalive = 5
