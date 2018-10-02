#encoding:utf-8

# dialect+driver://username:password@host：port/database
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = 'walter135790'
HOST = 'localhost'
PORT = '3306'
DATABASE = 'flask_auth'

# mysql 不会认识utf-8,而需要直接写成utf8
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
# SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db/db.sqlite'  # sqlite数据库位置
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

