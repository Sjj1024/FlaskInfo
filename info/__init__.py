from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from infoconfig import config

# 初始化数据库
db = SQLAlchemy()
def create_app(config_name):
    app = Flask(__name__)
    # 添加配置文件
    app.config.from_object(config[config_name])
    # 创建redis存储对象
    # 初始化数据库管理对象
    db.init_app(app)
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存的指定位置
    Session(app)
    return app