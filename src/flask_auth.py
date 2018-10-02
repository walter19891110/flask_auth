#!/usr/bin/env python

from flask import Flask, abort, jsonify
from flask_restful import reqparse
import myjwt
from models import db_config
from models.shared import db
from models.User import User
from models.DeviceInfo import DeviceInfo
import user_manager as um
import my_redis
import time

# 初始化
app = Flask(__name__)
app.config.from_object(db_config)
db.init_app(app)

redis_nodes = [{"host": "127.0.0.1", "port": "6379"},
               {"host": "127.0.0.1", "port": "6479"},
               {"host": "127.0.0.1", "port": "7379"},
               {"host": "127.0.0.1", "port": "7479"},
               {"host": "127.0.0.1", "port": "8379"},
               {"host": "127.0.0.1", "port": "8479"}
               ]

my_redis = my_redis.MyRedis(redis_nodes)


# *****************内部接口********************************* #
# *****************终端入网接口****************************** #


# 设置参数解析器
gr = reqparse.RequestParser()  #
gr.add_argument('devID', type=str, location='json')
gr.add_argument('devIC', type=str, location='json')
gr.add_argument('username', type=str, location='json')


@app.route('/api/dev/del_dev_user', methods=['PUT'])
def del_dev_user():
    """
    删除使用设备的用户
    :return: 返回结果代码
    """

    args = gr.parse_args()
    dev_id = args.get('devID')
    user_name = args.get('username')
    if dev_id is None or user_name is None:
        abort(400)  # missing arguments
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        abort(400)  # not existing
    dev.del_user(user_name)
    db.session.commit()
    return jsonify({'devID': dev.devID, 'userlist': dev.userlist})


@app.route('/api/dev/add_dev_info', methods=['POST'])
def add_dev_info():
    """
    添加设备信息
    :return: 添加的设备信息
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')
    r.add_argument('devIC', type=str, location='json')
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    dev_id = args.get('devID')
    dev_ic = args.get('devIC')
    user_name = args.get('username')
    if dev_id is None or dev_ic is None or user_name is None:
        abort(400)  # missing arguments
    if DeviceInfo.query.filter_by(devID=dev_id).first() is not None:
        abort(400)  # existing dev
    dev = DeviceInfo(devID=dev_id)
    dev.devIC = dev_ic
    dev.add_user(user_name)
    db.session.add(dev)
    db.session.commit()
    return jsonify({'devID': dev.devID, 'devIC': dev.devIC, 'userlist': dev.userlist})


@app.route('/api/dev/add_dev_user', methods=['POST'])
def add_dev_user():
    """
    添加设备使用的用户
    :return: 添加的设备信息
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    dev_id = args.get('devID')
    user_name = args.get('username')
    if dev_id is None or user_name is None:
        abort(400)  # missing arguments
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        abort(400)  # dev not existing
    dev.add_user(user_name)
    db.session.commit()
    return jsonify({'devID': dev.devID, 'devIC': dev.devIC, 'userlist': dev.userlist})


@app.route('/api/dev/del_dev_info', methods=['DELETE'])
def del_dev_info():
    """
    删除设备信息
    :return: 删除的设备信息
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')

    args = r.parse_args()
    dev_id = args.get('devID')
    if dev_id is None :
        abort(400)  # missing arguments
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        abort(400)  # not existing dev

    db.session.delete(dev)
    db.session.commit()
    return jsonify({'devID': dev.devID})


@app.route('/api/dev/get_dev_info', methods=['GET'])
def get_dev():
    """
    查询设备信息
    :return: 设备信息
    """

    dev_list = DeviceInfo.query.all()
    res = list()
    for i in dev_list:
        temp = {'devID': i.devID,
                'devIC': i.devIC,
                'userlist': i.userlist}
        res.append(temp)
    return jsonify({'res': res})


# =================外部接口================================= #
# =================用户管理接口============================== #
@app.route('/api/users/add_user', methods=['POST'])
def add_user():
    """添加用户
    
    :return: 执行结果代码
    {'ret_code': ret_code, 'msg': msg}
    """

    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')
    r.add_argument('password', type=str, location='json')
    r.add_argument('userrole', type=str, location='json')
    r.add_argument('userdesc', type=str, location='json')

    args = r.parse_args()
    result = um.add_user(dict(args.items()))
    return jsonify(result)


@app.route('/api/users/modify_user', methods=['PUT'])
def modify_user():
    """修改用户信息
    
    :return: 执行结果代码
    {'ret_code': ret_code, 'msg': msg}
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')
    r.add_argument('userrole', type=str, location='json')
    r.add_argument('userdesc', type=str, location='json')

    args = r.parse_args()
    result = um.modify_user(dict(args.items()))
    return jsonify(result)


@app.route('/api/users/modify_password', methods=['PUT'])
def modify_password():
    """修改用户信息

        :return: 执行结果代码
        {'ret_code': ret_code, 'msg': msg}
        """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')
    r.add_argument('oldpwd', type=str, location='json')
    r.add_argument('newpwd', type=str, location='json')

    args = r.parse_args()
    result = um.modify_password(dict(args.items()))
    return jsonify(result)


@app.route('/api/users/del_user', methods=['DELETE'])
def del_user():
    """删除用户
    
    :return: 执行结果代码
    {'ret_code': ret_code, 'msg': msg}
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    result = um.del_user(dict(args.items()))
    return jsonify(result)


@app.route('/api/users/get_user/<string:username>', methods=['GET'])
def get_user(username):
    """查询用户信息
    
    :return: 执行结果代码、用户信息
    {'ret_code': ret_code, 'msg': msg, 'username': user.username,
     'userrole': user.userrole, 'userdesc': user.userdesc}
    """

    result = um.get_user(username.strip('\"'))
    return jsonify(result)


@app.route('/api/auth/login_success', methods=['PUT'])
def login_success():
    """
    登录成功，更新登录状态，生成身份令牌，返回给用户
    :param username:登录成功的用户名
    :return: 身份令牌
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    user_name = args.get('username')
    if user_name is None:
        abort(400)
    user = User.query.filter_by(username=user_name).first()
    user_role = user.userrole

    # 更新登录状态 start #

    # 更新登录状态 end #

    # 生成身份令牌
    my_jwt = myjwt.MyJWT()
    access_token = my_jwt.create_token(user_name, user_role, 600).decode()  # 生成访问令牌，并把btyes转换为str
    refresh_token = my_jwt.create_token(user_name, user_role, 3600).decode()  # 生成刷新令牌，并把btyes转换为str
    return jsonify({'ret_code': 0, 'username': user_name, 'access_token': access_token, 'refresh_token': refresh_token})


# *****************终端入网接口****************************** #
@app.route('/api/dev/dev_verify', methods=['POST'])
def dev_verify():
    """
    终端入网验证
    :param devID:设备ID
    :param devIC: 设备识别码，设备类型为普通云终端时，此项为设备IP，设备类型为人机云终端时，此项为设备唯一识别码
    :return: 认证是否成功
    """
    # 设置参数解析器
    r = reqparse.RequestParser()
    r.add_argument('devID', type=str, location='json')
    r.add_argument('devIC', type=str, location='json')

    args = r.parse_args()
    dev_id = args.get('devID')
    dev_ic = args.get('devIC')
    if dev_id is None or dev_ic is None:
        abort(400)  # missing arguments
    dev_ic_db = my_redis.get(dev_id).decode()  # 从缓存中获取
    if dev_ic_db is None:
        # 缓存中没有，从数据库中获取
        dev = DeviceInfo.query.filter_by(devID=dev_id).first()
        if dev is None:
            abort(400)  # dev not exist
        dev_ic_db = dev.devIC
        print('mysql', dev.devIC)
        my_redis.set(dev_id, dev_ic_db, 600)  # 写入缓存
    ret_code = 0
    if dev_ic != dev_ic_db:
        ret_code = 1  # verify fail

    return jsonify({'ret_code': ret_code, 'devID': dev_id})


# *****************身份认证接口****************************** #
@app.route('/api/auth/id_verify', methods=['POST'])
def id_verify():
    """
    身份认证
    :param username:用户名
    :param type: 认证类型
    :param data: 认证凭证，用户密码，人脸数据等
    :return: 认证是否成功，用户名
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')
    r.add_argument('type', type=int, location='json')
    r.add_argument('data', type=str, location='json')

    args = r.parse_args()
    username = args.get('username')
    type = args.get('type')
    data = args.get('data')

    if username is None or type is None or data is None:
        abort(400)  # missing arguments
    verify_data = my_redis.get(username).decode()  # 从缓存中获取
    if verify_data is None:
        # 缓存中没有，从数据库中获取
        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(400)  # user not existing
        verify_data = user.password
        my_redis.set(username, verify_data, 600)
    ret_code = 0
    if type == 1:  # 用户名密码验证
        if not um.verify_password(data, verify_data):
            ret_code = 1

    return jsonify({'ret_code': ret_code, 'username': username})


# *****************身份令牌接口****************************** #
@app.route('/api/token/verify_token', methods=['POST'])
def verify_token():
    """
    令牌验证，验证令牌的合法性
    :param token: 访问令牌
    :return: 是否验证通过
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('token', type=str, location='json')

    args = r.parse_args()
    token = args.get('token').encode(encoding='utf-8')  # 将str转换为btyes
    if token is None:
        abort(400)  # missing arguments

    my_jwt = myjwt.MyJWT()
    res = my_jwt.verify_token(token)
    return jsonify({'ret_code': res})


@app.route('/api/token/update_token', methods=['POST'])
def update_token():
    """
    令牌更新，使用刷新令牌，请求新的访问令牌
    :param token: 刷新令牌
    :return: 访问令牌
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('token', type=str, location='json')

    args = r.parse_args()
    refresh_token = args.get('token').encode(encoding='utf-8')  # 将str转换为btyes
    if refresh_token is None:
        abort(400)  # missing arguments

    my_jwt = myjwt.MyJWT()
    res = my_jwt.refresh_token(refresh_token)
    if res[0] != 0:
        return jsonify({'ret_code': res[0]})
    return jsonify({'ret_code': res[0], 'access_token': res[1].decode()})


# *****************人机验证接口****************************** #
@app.route('/api/dev/user_dev_verify', methods=['POST'])
def user_dev_verify():
    """
    人机验证，根据设备ID，获取可以使用该设备的用户列表，看是否包含发送过来的用户，如果包含，则验证成功，否则返回失败
    :param devID:设备ID
    :param username: 用户名
    :return: 验证是否成功
    """
    # 设置参数解析器
    r = reqparse.RequestParser()
    r.add_argument('devID', type=str, location='json')
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    dev_id = args.get('devID')
    user_name = args.get('username')
    if dev_id is None or user_name is None:
        abort(400)  # missing arguments
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        abort(400)  # dev not existing
    ret_code = 0
    if not dev.verify_user(user_name):
        ret_code = 1

    return jsonify({'ret_code': ret_code, 'devID': dev_id, 'username': user_name})


# 其他辅助函数
@app.route('/api/test', methods=['POST'])
def test():
    # 设置参数解析器
    r = reqparse.RequestParser()
    r.add_argument('a', type=int, location='json')
    r.add_argument('b', type=int, location='json')

    args = r.parse_args()
    a = args.get('a')
    b = args.get('b')
    redis_start = time.time()
    ab = my_redis.get("wangjing")
    end = time.time()-redis_start
    print('redis:', end)
    mysql_start = time.time()
    user = User.query.filter_by(username="wangjing").first()
    end = time.time() - mysql_start
    print('mysql:', end)
    return jsonify({'result': a+b})


if __name__ == "__main__":

    print("flask auth api!")

    app.run(debug=True, ssl_context=(
        "../certs/server.crt.pem",
        "../certs/server.key.pem"))  # 调试时用，好处，修改代码后，不用重启程序

    # app.run(debug=True)
    # app.run(host='192.168.1.15')  # 正式使用时，设置服务器IP，接收全网的服务请求
