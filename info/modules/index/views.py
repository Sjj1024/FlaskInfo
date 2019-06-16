from flask import render_template, current_app, redirect, session

from info.models import User
from . import index_blu
from info import redis_store


@index_blu.route("/")
def index():
    # 取到用户id
    user_id = session.get("user_id", None)
    user = None
    if user_id:
        # 尝试查询用户的模型
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user": user.to_dict() if user else None
    }

    return render_template('news/index.html', data=data)

@index_blu.route("/favicon.ico")
def favicon():
    # 返回图标视图函数
    # 使用重定向即可获得图标：
    # return redirect("/static/news/favicon.ico")
    # 使用app的send_static_file进行设置，这是app的默认方法
    return current_app.send_static_file("news/favicon.ico")