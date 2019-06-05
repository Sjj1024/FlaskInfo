from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

class Config(object):
    SECRET_KEY = "asdadfafadfasdfa"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql/127.0.0.1:3306/fnews"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 配置redis的地址：
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 配置session存储在哪个数据库
    SESSION_TYPE = "redis"
    # 配置session的签名，让数据更安全
    SESSION_USE_SIGNER = True
    # 指定session保存的redis地址，
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session需要过期否
    SESSION_PERMANENT = False
    # 这是过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

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
    session["age"] = "18"
    return "hello world"


if __name__ == "__main__":
    manager.run()
