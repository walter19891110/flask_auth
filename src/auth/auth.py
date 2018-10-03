# 身份认证模块

from models.User import User
from usermanager import user_manager as um


def id_verify(auth_dict):
    """
    身份认证
    :param auth_dict:身份认证数据字典
    :return: 执行结果代码
    """

    ret_code = 0
    msg = 'OK'

    for v in auth_dict.values():
        if v is None:
            ret_code = 1
            msg = 'missing arguments!'
            return {'ret_code': ret_code, 'msg': msg}

    user_name = auth_dict.get('username')
    type = auth_dict.get('type')
    data = auth_dict.get('data')

    if type == 1:  # 用户名密码验证
        user = User.query.filter_by(username=user_name).first()
        if user is None:
            ret_code = 1
            msg = 'user not exist!'
            return {'ret_code': ret_code, 'msg': msg}
        verify_data = user.password
        if not um.verify_password(data, verify_data):
            ret_code = 1
            msg = 'verify fail!'

    return {'ret_code': ret_code, 'msg': msg}