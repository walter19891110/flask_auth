#!/usr/bin/env python

from flask import Flask
import my_redis
from devicemanager import dev_manager_api
from models import db_config
from models.shared import db
from usermanager import user_manager_api
from auth import auth_api
from mytoken import token_api

app = Flask(__name__)
app.config.from_object(db_config)
db.init_app(app)
app.register_blueprint(user_manager_api, url_prefix='/api/users')
app.register_blueprint(dev_manager_api, url_prefix='/api/dev')
app.register_blueprint(auth_api, url_prefix='/api/auth')
app.register_blueprint(token_api, url_prefix='/api/token')

redis_nodes = [{"host": "127.0.0.1", "port": "6379"},
               {"host": "127.0.0.1", "port": "6479"},
               {"host": "127.0.0.1", "port": "7379"},
               {"host": "127.0.0.1", "port": "7479"},
               {"host": "127.0.0.1", "port": "8379"},
               {"host": "127.0.0.1", "port": "8479"}
               ]

redis_cluster = my_redis.MyRedis(redis_nodes)


if __name__ == "__main__":

    print('flask auth api!')

    app.run(debug=True, ssl_context=(
        '../certs/server.crt.pem',
        '../certs/server.key.pem'))  # 调试时用，好处，修改代码后，不用重启程序

    # app.run(debug=True)
    # app.run(host='192.168.1.15')  # 正式使用时，设置服务器IP，接收全网的服务请求
