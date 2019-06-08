from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from infoconfig import config
import logging

# 设置log日志加载配置
def set_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 初始化数据库
db = SQLAlchemy()

# 声明redis_store是一个实例对象
redis_store = StrictRedis() # type:StrictRedis
def create_app(config_name):
    # 让log日志文件在创建app的时候就运行
    set_log(config_name)
    app = Flask(__name__)
    # 添加配置文件
    app.config.from_object(config[config_name])
    # 创建redis存储对象
    # 初始化数据库管理对象
    db.init_app(app)
    # 配置redis 的存储位置
    global redis_store  # 声明redis_store为全局变量
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存的指定位置
    Session(app)
    # 导入蓝图,然后和app关联，在使用的时候导入，就不会产生循环导入的问题了
    from info.modules.index import index_blu
    # 配置好这个app之后，就返回这个app
    app.register_blueprint(index_blu)
    return app