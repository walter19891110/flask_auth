# 用户管理模块

from mytoken import my_token
from flask import jsonify
from flask_restful import reqparse
from passlib.apps import custom_app_context as pwd_context
from models.User import User
from models.shared import db
from . import user_manager_api


# ========================外部接口========================== #
@user_manager_api.route('/add_user', methods=['POST'])
def add_user_api():
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
    result = add_user(dict(args.items()))
    return jsonify(result)


@user_manager_api.route('/modify_user', methods=['PUT'])
def modify_user_api():
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
    result = modify_user(dict(args.items()))
    return jsonify(result)


@user_manager_api.route('/modify_password', methods=['PUT'])
def modify_password_api():
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
    result = modify_password(dict(args.items()))
    return jsonify(result)


@user_manager_api.route('/del_user', methods=['DELETE'])
def del_user_api():
    """删除用户

    :return: 执行结果代码
    {'ret_code': ret_code, 'msg': msg}
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    result = del_user(dict(args.items()))
    return jsonify(result)


@user_manager_api.route('/get_user/<string:username>', methods=['GET'])
def get_user_api(username):
    """查询用户信息

    :return: 执行结果代码、用户信息
    {'ret_code': ret_code, 'msg': msg, 'username': user.username,
     'userrole': user.userrole, 'userdesc': user.userdesc}
    """

    result = get_user(username.strip('\"'))
    return jsonify(result)


@user_manager_api.route('/login_success', methods=['PUT'])
def login_success_api():
    """
    登录成功，更新登录状态，生成身份令牌，返回给用户
    :param username:登录成功的用户名
    :return: 身份令牌
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('username', type=str, location='json')

    args = r.parse_args()
    result = login_success(dict(args.items()))
    return jsonify(result)


# ========================内部函数========================== #
def encrypt_password(password):
    """密码散列
    
    :param password: 明文密码
    :param password: str
    :return 密文密码
    :rtype: str
    """

    return pwd_context.encrypt(password)


def verify_password(password, en_password):
    """对明密文密码进行验证
    
    :param password: 明文密码
    :param en_password: 密文密码
    :return: 密码正确返回True，密码错误返回False验证结果
    :rtype: Bool
    """

    return pwd_context.verify(password, en_password)


def add_user(user_dict):
    """添加用户
    
    :param user_dict: 用户信息
    :type user_dict: dict
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"

    for v in user_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    username = user_dict.get('username')
    if User.query.filter_by(username=username).first() is not None:
        ret_code = 1
        msg = 'username already exist!'
        return {'ret_code': ret_code, 'msg': msg}
    else:
        user = User(username=username)
        user.password = encrypt_password(user_dict.get('password'))
        user.userrole = user_dict.get('userrole')
        user.userdesc = user_dict.get('userdesc')
        db.session.add(user)
        db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def modify_user(user_dict):
    """修改用户信息
    
    :param user_dict: 用户信息
    :type user_dict: dict
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"
    username = user_dict.get('username')
    if username is None:
        ret_code = 1
        msg = 'missing arguments!'
        return {'ret_code': ret_code, 'msg': msg}

    user = User.query.filter_by(username=username).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    userrole = user_dict.get('userrole')
    if userrole is not None:
        user.userrole = userrole
    userdesc = user_dict.get('userdesc')
    if userdesc is not None:
        user.userdesc = userdesc

    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def modify_password(user_dict):
    """修改用户密码

    :param user_dict: 用户名，原密码，新密码
    :type user_dict: dict
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"
    username = user_dict.get('username')
    if username is None:
        ret_code = 1
        msg = 'missing arguments!'
        return {'ret_code': ret_code, 'msg': msg}

    for v in user_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    user = User.query.filter_by(username=username).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}
    old_password = user_dict.get('oldpwd')
    new_password = user_dict.get('newpwd')
    if not verify_password(old_password, user.password):
        ret_code = 1
        msg = 'old password error!'
        return {'ret_code': ret_code, 'msg': msg}

    user.password = encrypt_password(new_password)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def del_user(user_dict):
    """删除用户信息

    :param user_dict: 用户名
    :type user_dict: dict
    :return: 执行结果代码
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"
    username = user_dict.get('username')
    if username is None:
        ret_code = 1
        msg = 'missing arguments!'
        return {'ret_code': ret_code, 'msg': msg}

    user = User.query.filter_by(username=username).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    db.session.delete(user)
    db.session.commit()

    return {'ret_code': ret_code, 'msg': msg}


def get_user(user_name):
    """获取用户信息
    
    :param user_name: 用户名
    :type user_name: str
    :return: 执行结果代码和用户信息
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"

    user = User.query.filter_by(username=user_name).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    return {'ret_code': ret_code, 'msg': msg, 'username': user.username,
            'userrole': user.userrole, 'userdesc': user.userdesc}


def login_success(user_dict):
    """登录成功，更新登录状态，生成身份令牌，返回给用户
    
    :param user_dict: 用户名
    :type user_dict: dict
    :return: 执行结果代码、身份令牌
    :rtype: dict
    """

    ret_code = 0
    msg = "OK"
    user_name = user_dict.get('username')
    if user_name is None:
        ret_code = 1
        msg = 'missing arguments!'
        return {'ret_code': ret_code, 'msg': msg}

    user = User.query.filter_by(username=user_name).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    user_role = user.userrole

    # 更新登录状态 start #

    # 更新登录状态 end #

    # 生成身份令牌
    access_token = my_token.create_token(user_name, user_role, 600)  # 生成访问令牌，并把btyes转换为str
    refresh_token = my_token.create_token(user_name, user_role, 3600)  # 生成刷新令牌，并把btyes转换为str
    return {'ret_code': ret_code, 'msg': msg, 'access_token': access_token,
            'refresh_token': refresh_token}


