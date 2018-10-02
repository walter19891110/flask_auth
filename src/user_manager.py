# 用户管理类，负责用户的增删改查

from models.shared import db
from models.User import User
from passlib.apps import custom_app_context as pwd_context


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




