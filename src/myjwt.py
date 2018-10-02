
import os
import time
import itsdangerous

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(parent_dir, "data")


class MyJWT():

    def create_token(self, user, role, expires):
        """生成Token

        Args:
            user: 用户名
            role: 用户角色
            expires: Token有效期，int型，单位s
        Return: 
            token: 生成的Token
        """

        # 序列化JWT的Header和Signature
        s = itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key="SECERT_KEY",
            salt="AUTH_SALT",
            expires_in=expires)

        timestamp = time.time()  # 当前时间
        data = {"user_id":user, "user_role":role, "iat":timestamp}  # 设置Payload的内容
        token = s.dumps(data)  # 生成完整的JWT格式的Token
        # print(data)
        return token

    def analysis_token(self, token):
        """解析令牌

        Args:
            token: 待解析的令牌
        Return: 
            user: token中的用户名
        """

        s = itsdangerous.TimedJSONWebSignatureSerializer(
            secret_key="SECERT_KEY",
            salt="AUTH_SALT")

        res = [0, None, None]

        try:
            data = s.loads(token)
        except itsdangerous.SignatureExpired:
            msg = "Token expired!"
            res[0] = 1
            print(msg)
            return res
        except itsdangerous.BadSignature as e:
            encode_payload = e.payload
            if encode_payload is not None:
                try:
                    s.load_payload(encode_payload)
                except itsdangerous.BadData:
                    msg = "Token tampered!"
                    res[0] = 2
                    print(msg)
                    return res
            msg = "BadSignature of token!"
            res[0] = 3
            print(msg)
            return res
        except Exception:
            msg = "Wrong token with unknown reason!"
            res[0] = 4
            print(msg)
            return res

        if ("user_id" not in data) or ("user_role" not in data):
            msg = "Illegal payload inside!"
            res[0] = 5
            print(msg)
            return res

        msg = "token analysis success!"
        print(msg)
        res[1] = data["user_id"]
        res[2] = data["user_role"]
        return res

    def refresh_token(self, ref_token):
        """刷新令牌
           使用刷新令牌，生成新的访问令牌
        Args:
            ref_token: 刷新令牌
        Return: 
            acc_token: 新的访问令牌
        """

        res = self.analysis_token(ref_token)  # 解析刷新令牌
        result = [0, None]
        if res[0] is not 0:  # 如果res[0]不为0，说明令牌解析失败，返回错误码
            result[0] = res[0]
            return result

        user = res[1]
        role = res[2]
        acc_token = self.create_token(user, role, 20)
        result[1] = acc_token
        return result

    def verify_token(self, token):
        """验证令牌
        Args:
            token: 待验证的令牌
        Return: 
            res_code: 验证结果
        """

        res = self.analysis_token(token)
        res_code = res[0]
        return res_code


if __name__ == "__main__":

    print("test jwt!")
    my_jwt = MyJWT()
    access_token = my_jwt.create_token("wangjing", "admin", 3)
    refresh_token = my_jwt.create_token("wangjing", "admin", 1000)
    print(access_token)
    print(refresh_token)
    #time.sleep(5)
    access_res = my_jwt.analysis_token(access_token)
    print(access_res)
    refresh_res = my_jwt.analysis_token(refresh_token)
    print(refresh_res)

    # 如果令牌超时，则重新生成访问令牌
    if access_res[0] is 0:
        res = my_jwt.refresh_token(refresh_token)
        ac = my_jwt.analysis_token(res[1])
        print(ac)

    a = 'g'
    u = 'admin'
    if len(a) != 0:
        l = a.split(',')
        l.append(u)
        s = ','.join(l)
    else:
        s = u
    print(s)
    s = 'g'
    l1 = s.split(',')
    for i in l1:
        if i == a:
            l1.remove(i)
    print(len(u))

