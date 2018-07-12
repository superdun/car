# -*- coding: utf-8 -*-
from datetime import timedelta
DEBUG = False
SQLALCHEMY_ECHO = False
PER_PAGE = 32
UPLOAD_URL = 'static/upload'
PREVIEW_THUMBNAIL = '-preview'
API_PREFIX = "/api"
LOGIN_TIME_OUT = 3600
CACHE_TYPE = "redis"
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
JWT_AUTH_URL_RULE = "/api/login"
JWT_EXPIRATION_DELTA = timedelta(seconds=3000)
VCODE_TIMEOUT  = 300
CAR_CACHE_TIMEOUT  = 15
GPS_CACHE_TIMEOUT  = 3600
ORDER_STATUS={"ok":[u"已支付",[u"查看订单",u"申请退款"],'black'],"waiting":[u"待支付",[u"去支付",u"取消订单"],'red'],"refunding":[u"正在退款",[u"查看订单"],'black'],"refunded":[u"已退款",[u"查看订单"],'black'],"refundfailed":[u"退款失败",[u"查看订单"],'black'],"canceled":[u"已取消",[u"查看订单"],'grey']}
BABEL_DEFAULT_LOCALE = "zh_CN"