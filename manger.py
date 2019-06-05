from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql/127.0.0.1:3306/fnews"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)
# 添加配置文件
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)

@app.route("/")
def index():
    return "hello world"


if __name__ == "__main__":
    app.run()
