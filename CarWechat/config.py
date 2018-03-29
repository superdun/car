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
SESSION_TYPE = 'redis'
SESSION_REDIS = ''
