from flask import render_template, current_app, redirect, session

from info.models import User, News
from . import index_blu
from info import redis_store, constants


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

    # 右侧的新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 定义一个空的字典列表，里面装的就是字典
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_li": news_dict_li
    }

    return render_template('news/index.html', data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # 返回图标视图函数
    # 使用重定向即可获得图标：
    # return redirect("/static/news/favicon.ico")
    # 使用app的send_static_file进行设置，这是app的默认方法
    return current_app.send_static_file("news/favicon.ico")