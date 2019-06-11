import random
import re

from flask import request, current_app, make_response, jsonify

from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import pass_blue

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
        redis_store.set("SMS_"+mobil, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    # 否则的话，告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")


