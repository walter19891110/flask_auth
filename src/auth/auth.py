# 身份认证模块

from mytoken import my_token
from flask import jsonify
from flask_restful import reqparse
from models.User import User
from usermanager import user_manager as um
from . import auth_api


# ========================外部接口========================== #
# ======================身份认证接口========================= #
@auth_api.route('/id_verify', methods=['POST'])
def id_verify_api():
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
    result = id_verify(dict(args.items()))
    return jsonify(result)


# =======================内部接口=========================== #
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

    user = User.query.filter_by(username=user_name).first()
    if user is None:
        ret_code = 1
        msg = 'user not exist!'
        return {'ret_code': ret_code, 'msg': msg}

    verify_data = user.password
    if type == 1:  # 用户名密码验证
        if not um.verify_password(data, verify_data):
            ret_code = 1
            msg = 'verify fail!'

    return {'ret_code': ret_code, 'msg': msg}