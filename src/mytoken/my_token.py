# 身份令牌模块
import time
import itsdangerous
from flask import jsonify
from flask_restful import reqparse
from . import token_api


# ========================外部接口========================== #
# ======================身份令牌接口========================= #
@token_api.route('/verify_token', methods=['POST'])
def verify_token_api():
    """令牌验证，验证令牌的合法性
    
    :param token: 访问令牌
    :return: 是否验证通过
    """
    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('token', type=str, location='json')

    args = r.parse_args()
    token = args.get('token')
    ret_code = 0
    msg = 'OK'
    if token is None:
        ret_code = 1
        msg = 'missing arguments!'
        return jsonify({'ret_code': ret_code, 'msg': msg})

    return jsonify(verify_token(token))


@token_api.route('/update_token', methods=['POST'])
def update_token_api():
    """令牌更新，使用刷新令牌，请求新的访问令牌
    
    :param token: 刷新令牌
    :return: 访问令牌
    """

    # 设置参数解析器
    r = reqparse.RequestParser()  #
    r.add_argument('token', type=str, location='json')

    args = r.parse_args()
    token = args.get('token')
    if token is None:
        ret_code = 1
        msg = 'missing arguments!'
        return jsonify({'ret_code': ret_code, 'msg': msg})

    return jsonify(update_token(token))


# =======================内部接口=========================== #
def create_token(user, role, expires):
    """生成Token

    :param user: 用户名
    :param role: 用户角色
    :param expires: Token有效期，int型，单位s
    :return :
        token: 生成的Token
    """

    # 序列化JWT的Header和Signature
    s = itsdangerous.TimedJSONWebSignatureSerializer(
        secret_key='SECERT_KEY',
        salt='AUTH_SALT',
        expires_in=expires)

    timestamp = time.time()  # 当前时间
    data = {"user_id": user, "user_role": role, "iat": timestamp}  # 设置Payload的内容
    token = s.dumps(data).decode()  # 生成完整的JWT格式的Token，并把btyes转换为str
    # print(data)
    return token


def analysis_token(token):
    """解析令牌

    :param token: 待解析的令牌
    :type : str
    :return: 
        user: token中的用户名
        role: token中的用户角色
    """

    s = itsdangerous.TimedJSONWebSignatureSerializer(
        secret_key='SECERT_KEY',
        salt='AUTH_SALT')

    ret_code = 0
    msg = 'OK'
    try:
        data = s.loads(token.encode(encoding='utf-8'))  # 将str转换为btyes，进行解析
    except itsdangerous.SignatureExpired:
        ret_code = 1
        msg = 'Token expired!'
        return {'ret_code': ret_code, 'msg': msg}
    except itsdangerous.BadSignature as e:
        encode_payload = e.payload
        if encode_payload is not None:
            try:
                s.load_payload(encode_payload)
            except itsdangerous.BadData:
                ret_code = 2
                msg = 'Token tampered!'
                return {'ret_code': ret_code, 'msg': msg}
        ret_code = 3
        msg = 'BadSignature of token!'
        print(msg)
        return {'ret_code': ret_code, 'msg': msg}
    except Exception:
        ret_code = 4
        msg = 'Wrong token with unknown reason!'
        print(msg)
        return {'ret_code': ret_code, 'msg': msg}

    if ('user_id' not in data) or ('user_role' not in data):
        ret_code = 5
        msg = 'Illegal payload inside!'
        print(msg)
        return {'ret_code': ret_code, 'msg': msg}

    return {'ret_code': ret_code, 'msg': msg, 'user': data['user_id'], 'role': data['user_role']}


def update_token(ref_token):
    """刷新令牌
       使用刷新令牌，生成新的访问令牌
    :param ref_token: 刷新令牌
    :type : str
    :return: 
        acc_token: 新的访问令牌
    """
    print(ref_token)
    res = analysis_token(ref_token)  # 解析刷新令牌
    print(res)
    ret_code = 0
    msg = 'OK'
    if res.get('ret_code') is not 0:  # 如果res[0]不为0，说明令牌解析失败，返回错误码
        return res

    user = res.get('user')
    role = res.get('role')
    acc_token = create_token(user, role, 20)
    return {'ret_code': ret_code, 'msg': msg, 'access_token': acc_token}


def verify_token(token):
    """验证令牌

    :param token: 待验证的令牌
    :type :str
    :return: 
        res_code: 验证结果
    """

    res = analysis_token(token)
    return {'ret_code': res.get('ret_code'), 'msg': res.get('msg')}


if __name__ == "__main__":

    print('test jwt!')
    access_token = create_token('wangjing', 'admin', 3)
    refresh_token = create_token('wangjing', 'admin', 1000)
    print(type(access_token), access_token)
    print(type(refresh_token), refresh_token)
    #time.sleep(5)
    access_res = analysis_token(access_token)
    print(access_res)
    refresh_res = analysis_token(refresh_token)
    print(refresh_res)

    # 如果令牌超时，则重新生成访问令牌
    if access_res.get('ret_code') is 0:
        res = update_token(refresh_token)
        print(res)
        ac = analysis_token(res.get('access_token'))
        print(ac)


