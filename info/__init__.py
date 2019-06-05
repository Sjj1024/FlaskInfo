from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
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