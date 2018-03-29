from flask import current_app
from werkzeug.contrib.cache import RedisCache

host = current_app.config.get("REDIS_HOST")
port = current_app.config.get("REDIS_PORT")
cache =  RedisCache(host,port)