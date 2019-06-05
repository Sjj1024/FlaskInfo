from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from infoconfig import Config

app = Flask(__name__)
# 添加配置文件
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)
# 创建redis存储对象
redis_store = StrictRedis(app)
# 开启CSRF保护
CSRFProtect(app)
# 设置session保存的指定位置
Session(app)
# 设置manger管理对象
manager = Manager(app)
# 配置数据库迁移设置,关联app和db
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():
    print(11111)
    session["age"] = "18"
    return "hello world"


if __name__ == "__main__":
    manager.run()
