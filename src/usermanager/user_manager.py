# 用户管理模块

from mytoken import my_token
from passlib.apps import custom_app_context as pwd_context
from models.User import User
from models.shared import db


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


