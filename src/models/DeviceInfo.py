from models.shared import db


class DeviceInfo(db.Model):
    """
    设备信息表，存储云终端的设备ID，设备识别码，可使用该设备的用户名列表
    """
    # 定义表名
    __tablename__ = 'device_info'
    # 定义列对象
    devID = db.Column(db.String(256), primary_key=True)  # 设备ID
    devIC = db.Column(db.String(256))  # 设备识别码
    userlist = db.Column(db.Text)  # 可使用该设备的用户名列表，用户名之间用逗号隔开

    def get_userlist(self):
        return self.userlist.split(',')

    def add_user(self, username):
        """
        将某个用户添加到可以使用该设备的用户名列表中
        :param username: 用户名
        :return: 添加后的用户名列表
        """
        if self.userlist is not None:
            user_list = self.userlist.split(',')
            if username not in user_list:
                user_list.append(username)
                self.userlist = ','.join(user_list)  # 将用户名用逗号连接
        else:
            self.userlist = username

    def del_user(self, username):
        """
        将某个用户从可以使用该设备的用户名列表中删除
        :param username: 用户名
        :return: 更新后的用户名列表
        """
        if self.userlist is not None:
            user_list = self.userlist.split(',')
            for user in user_list:
                if user == username:
                    user_list.remove(username)
            if len(user_list) != 0:
                self.userlist = ','.join(user_list)  # 将用户名用逗号连接

    def verify_ic(self, dev_ic):
        if dev_ic != self.devIC:
            return False
        return True

    def verify_user(self, username):
        if self.userlist is not None:
            user_list = self.userlist.split(',')
            for user in user_list:
                if user == username:
                    return True
        return False

