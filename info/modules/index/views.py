from flask import render_template, current_app, redirect
from . import index_blu
from info import redis_store


@index_blu.route("/")
def index():
    return render_template("news/index.html")

@index_blu.route("/favicon.ico")
def favicon():
    # 返回图标视图函数
    # 使用重定向即可获得图标：
    # return redirect("/static/news/favicon.ico")
    # 使用app的send_static_file进行设置，这是app的默认方法
    return current_app.send_static_file("news/favicon.ico")