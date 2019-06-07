# 将视图函数抽取到蓝图这里
from flask import Blueprint

# 定义蓝图实例对象，index是蓝图名字
index_blu = Blueprint("index", __name__)

# 使用相对路径.导入views所有
from .views import *