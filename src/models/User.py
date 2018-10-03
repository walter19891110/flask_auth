from models.shared import db


class User(db.Model):
    """用户基本信息表
    """
    # 定义表名
    __tablename__ = 'users'
    # 定义列对象
    username = db.Column(db.String(256), primary_key=True)
    password = db.Column(db.String(256))
    userrole = db.Column(db.String(256))
    userdesc = db.Column(db.String(256))


class UserLogin(db.Model):
    """用户登录信息表
    """
    # 定义表名
    __tablename__ = 'user_login'
    # 定义列对象
    username = db.Column(db.String(256), primary_key=True)
    loginstatus = db.Column(db.String(256))
    logintime = db.Column(db.String(256))