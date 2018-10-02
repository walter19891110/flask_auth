# 使用gunicorn运行flask程序

import multiprocessing
import gevent.monkey

gevent.monkey.patch_all()

debug = True
loglevel = 'debug'
bind = '127.0.0.1:5000'
pidfile = '../log/gunicorn.pid'
logfile = '../log/debug.log'

# 启动的进程数, 设置gevent模式，使其支持协程，用于高并发
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1  # 测试时用
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

# 设置服务器证书，使其支持https
certfile = '../certs/server.crt.pem'
keyfile = '../certs/server.key.pem'
