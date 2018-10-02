# 设备管理模块，实现终端验证和人机验证功能

from models.shared import db
from models.DeviceInfo import DeviceInfo
from flask import jsonify
from flask_restful import reqparse
import my_redis
from . import dev_manager_api

redis_nodes = [{"host": "127.0.0.1", "port": "6379"},
               {"host": "127.0.0.1", "port": "6479"},
               {"host": "127.0.0.1", "port": "7379"},
               {"host": "127.0.0.1", "port": "7479"},
               {"host": "127.0.0.1", "port": "8379"},
               {"host": "127.0.0.1", "port": "8479"}
               ]

redis_cluster1 = my_redis.MyRedis(redis_nodes)


# =======================外部接口=========================== #
# =====================终端入网接口========================== #
@dev_manager_api.route('/dev_verify', methods=['POST'])
def dev_verify_api():
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
    result = dev_verify(dict(args.items()))
    return jsonify(result)


# =====================人机验证接口========================== #
@dev_manager_api.route('/user_dev_verify', methods=['POST'])
def user_dev_verify_api():
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
    result = user_dev_verify(dict(args.items()))
    return jsonify(result)


# =======================内部接口=========================== #
@dev_manager_api.route('/del_dev_user', methods=['PUT'])
def del_dev_user_api():
    """
    删除使用设备的用户
    :return: 返回结果代码
    """

    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    result = del_dev_user(dict(args.items()))
    return jsonify(result)


@dev_manager_api.route('/add_dev_info', methods=['POST'])
def add_dev_info_api():
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
    result = add_dev_info(dict(args.items()))
    return jsonify(result)


@dev_manager_api.route('/add_dev_user', methods=['POST'])
def add_dev_user_api():
    """
    添加设备使用的用户
    :return: 添加的设备信息
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    result = add_dev_user(dict(args.items()))
    return jsonify(result)


@dev_manager_api.route('/del_dev_info', methods=['DELETE'])
def del_dev_info_api():
    """
    删除设备信息
    :return: 删除的设备信息
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('devID', type=str, location='json')

    args = r.parse_args()
    result = del_dev_info(dict(args.items()))
    return jsonify(result)


@dev_manager_api.route('/get_dev_info', methods=['GET'])
def get_dev_api():
    """
    查询设备信息
    :return: 设备信息
    """
    return jsonify(get_dev())


# ========================内部函数========================== #
def dev_verify(dev_dict):
    """终端入网验证
    
    :param dev_dict:设备信息
    :type: duct
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = 'OK'
    for v in dev_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    dev_id = dev_dict.get('devID')
    dev_ic = dev_dict.get('devIC')
    dev_ic_db = redis_cluster1.get(dev_id)  # 从缓存中获取
    if dev_ic_db is None:
        # 缓存中没有，从数据库中获取
        dev = DeviceInfo.query.filter_by(devID=dev_id).first()
        if dev is None:
            ret_code = 1
            msg = 'dev not exist!'
            return {'ret_code': ret_code, 'msg': msg}
        dev_ic_db = dev.devIC
        redis_cluster1.set(dev_id, dev_ic_db, 600)  # 写入缓存
    else:
        dev_ic_db = dev_ic_db.decode()  # 将从redis中取出的btyes转换为str

    if dev_ic != dev_ic_db:
        ret_code = 1
        msg = 'dev verify fail!'

    return {'ret_code': ret_code, 'msg': msg}


# =====================人机验证接口========================== #

def user_dev_verify(dev_dict):
    """终端入网验证
    
    :param dev_dict:设备信息
    :type: duct
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = 'OK'
    for v in dev_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    dev_id = dev_dict.get('devID')
    user_name = dev_dict.get('username')
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        ret_code = 1
        msg = 'dev not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    if not dev.verify_user(user_name):
        ret_code = 1
        msg = 'user dev verify fail!'

    return {'ret_code': ret_code, 'msg': msg}


# =======================内部接口=========================== #
def del_dev_user(dev_dict):
    """
    删除使用设备的用户
    :return: 返回结果代码
    """

    ret_code = 0
    msg = 'OK'
    for v in dev_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    dev_id = dev_dict.get('devID')
    user_name = dev_dict.get('username')
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        ret_code = 1
        msg = 'dev not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    dev.del_user(user_name)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def add_dev_info(dev_dict):
    """
    添加设备信息
    :return: 添加的设备信息
    """

    ret_code = 0
    msg = 'OK'
    for v in dev_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    dev_id = dev_dict.get('devID')
    dev_ic = dev_dict.get('devIC')
    user_name = dev_dict.get('username')
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is not None:
        ret_code = 1
        msg = 'dev exist!'
        return {'ret_code': ret_code, 'msg': msg}

    dev = DeviceInfo(devID=dev_id)
    dev.devIC = dev_ic
    dev.add_user(user_name)
    db.session.add(dev)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def add_dev_user(dev_dict):
    """
    添加设备使用的用户
    :return: 添加的设备信息
    """

    ret_code = 0
    msg = 'OK'
    for v in dev_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    dev_id = dev_dict.get('devID')
    user_name = dev_dict.get('username')
    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        ret_code = 1
        msg = 'dev not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    dev.add_user(user_name)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def del_dev_info(dev_dict):
    """
    删除设备信息
    :return: 删除的设备信息
    """

    ret_code = 0
    msg = 'OK'
    dev_id = dev_dict.get('devID')
    if dev_id is None:
        ret_code = 1
        msg = 'missing arguments!'
        return {'ret_code': ret_code, 'msg': msg}

    dev = DeviceInfo.query.filter_by(devID=dev_id).first()
    if dev is None:
        ret_code = 1
        msg = 'dev not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    db.session.delete(dev)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


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
    return {'ret_code': 0, 'msg': 'OK', 'devlist': res}

