import multiprocessing
import os.path

def numCPUs():
    return multiprocessing.cpu_count() * 2 + 1

bind = "127.0.0.1:8000"
pidfile     = os.path.expanduser("~/webpi/logs/gunicorn.pid")
logfile     = os.path.expanduser("~/webpi/logs/production.log"
accesslog   = os.path.expanduser("~/webpi/logs/production.log"
errorlog    = os.path.expanduser("~/webpi/logs/errors.log"
loglevel    = "debug"
name        = "webpi"
timeout     = 120
max_requests = 1000
workers     = numCPUs()