# 首次部署该程序时，先执行该文件，创建表
from src.models.shared import db

if __name__ == "__main__":
    db.create_all()