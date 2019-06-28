import functools

from flask import session, g


def do_index_class(index):
    """自定义过滤器，过滤点击排序html的class"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""

def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 获取到当前登录用户的id
        user_id = session.get("user_id")
        # 通过id获取用户信息
        user = None
        if user_id:
            from info.models import User
            user = User.query.get(user_id)

        g.user = user
        return f(*args, **kwargs)

    return wrapper