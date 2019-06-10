from flask import request, current_app, make_response, jsonify

from info import redis_store, constants
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