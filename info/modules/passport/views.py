import random
import re

from datetime import datetime
from flask import request, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import pass_blue


@pass_blue.route('/logout')
def logout():
    """
    退出登录
    :return:
    """
    # pop是移除session中的数据(dict)
    # pop 会有一个返回值，如果要移除的key不存在，就返回None
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


@pass_blue.route("/login", methods=["POST"])
def login():
    """
    登录
    1. 获取参数
    2. 校验参数
    3. 校验密码是否正确
    4. 保存用户的登录状态
    5. 响应
    :return:
    """

    # 1. 获取参数
    params_dict = request.json
    mobile = params_dict.get("mobile")
    password = params_dict.get("password")

    # 2. 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 校验手机号是否正确
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 校验密码是否正确
    # 先查询出当前是否有指定手机号的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    # 校验登录的密码和当前用户的密码是否一致
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或者密码错误")

    # 4. 保存用户的登录状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 设置当前用户最后一次登录的时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    # 5. 响应
    return jsonify(errno=RET.OK, errmsg="登录成功")

@pass_blue.route('/register', methods=["POST"])
def register():
    """
    注册的逻辑
    1. 获取参数
    2. 校验参数
    3. 取到服务器保存的真实的短信验证码内容
    4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    5. 如果一致，初始化 User 模型，并且赋值属性
    6. 将 user 模型添加数据库
    7. 返回响应
    :return:
    """
    # 1. 获取参数
    param_dict = request.json
    mobile = param_dict.get("mobile")
    smscode = param_dict.get("smscode")
    password = param_dict.get("password")

    # 2. 校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数")

    # 校验手机号是否正确
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 取到服务器保存的真实的短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    # 4. 校验用户输入的短信验证码内容和真实验证码内容是否一致
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5. 如果一致，初始化 User 模型，并且赋值属性
    user = User()
    user.mobile = mobile
    # 暂时没有昵称 ，使用手机号代替
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # 对密码做处理
    user.password = password

    # 6. 添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往 session 中保存数据表示当前已经登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@pass_blue.route("/image_code")
def image_cade():
    """
    步骤：
    获取参数
    生成验证码
    删除之前验证码并保存当前验证码
    错误处理
    响应返回
    :return:
    """
    # 获取到图片参数id
    code_id = request.args.get('image_CodeId')
    # 生成图片验证码
    name, text, image = captcha.generate_captcha()
    print(text)
    # 删除之前验证码
    try:
        # 保存当前生成的图片验证码内容
        redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))
    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@pass_blue.route("/sms_code", methods=["POST"])
def sms_code():
    """
    1.接收前端发送过来的参数，手机号，图片验证码（当点击发送验证码才会得到）
    2.整体校验参数的完整性
    3.单独校验参数的准确性
    4.校验图片验证码是否正确，若不正确，则返回
    5.删除图片验证码
    6.生成短信验证码，使用第三方发送短信验证码
    :return:
    """
    # return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    params_dict = request.json
    mobil = params_dict.get("mobile")
    image_cade = params_dict.get("imageCode")
    image_cade_id = params_dict.get("imageCodeId")
    # 整体效验参数的正确性
    if not all([mobil, image_cade, image_cade_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 效验手机号的正确性
    if not re.match(r"1[34567]\d{9}", mobil):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式不正确")
    # 效验短信验证码的正确
    # 从redis中获取图片验证码,然后做比对
    try:
        image_code_redis = redis_store.get('ImageCode_' + image_cade_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库库查询失败")
    # 如果没有查询到图片验证码，说明 图片验证码已过期
    if not image_code_redis:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")
    # 然后做图片验证码比对操作
    if image_cade.upper() != image_code_redis.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入不正确")

    # 如果图片验证码查询正确,生成短信验证码
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码为:%s" % sms_code_str)
    # 开始调用发送短信验证码
    # result = CCP().send_template_sms(mobil, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES], 1)
    # # 判断发送结果
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    # 将短信验证码保存到redis中
    try:
        redis_store.set("SMS_" + mobil, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    # 否则的话，告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")
