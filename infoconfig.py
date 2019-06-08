from redis import StrictRedis
import logging

class Config(object):
    SECRET_KEY = "asdadfafadfasdfa"
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/fnews"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 配置redis的地址：
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 配置session存储在哪个数据库
    SESSION_TYPE = "redis"
    # 配置session的签名，让数据更安全
    SESSION_USE_SIGNER = True
    # 指定session保存的redis地址，
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session需要过期否
    SESSION_PERMANENT = False
    # 这是过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


class Development(Config):
    """开发环境下的配置"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class Production(Config):
    """z生产环境下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.ERROR


class Testing(Config):
    """测试环境下的配置"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = True


config = {
    "development": Development,
    "production": Production,
    "testing": Testing
}
