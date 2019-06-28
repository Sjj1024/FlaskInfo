from flask import render_template

from . import news_blu


@news_blu.route('/<int:news_id>')
def news_detail(news_id):
    data = {}
    return render_template('news/detail.html', data = data)