from models.shared import db
from passlib.apps import custom_app_context as pwd_context


class User(db.Model):
    """
    用户名密码表
    生成用户名密码表
    提供相应的操作
    """
    # 定义表名
    __tablename__ = 'users'
    # 定义列对象
    username = db.Column(db.String(256), primary_key=True)
    password = db.Column(db.String(256))
    userrole = db.Column(db.String(256))
    userdesc = db.Column(db.String(256))

    def set_password(self, password):
        """
        密码散列
        :param password: 明文密码
        """
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        """
        接受一个明文的密码作为参数并且当密码正确的话返回 True 
        或者密码错误的话返回 False。
        :param password: 明文密码
        :return: 验证结果
        """
        return pwd_context.verify(password, self.password)

