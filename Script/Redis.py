from flask import current_app
import redis
import config
def redis_client():
    host = config.REDIS_HOST
    port = config.REDIS_PORT
    return redis.StrictRedis(host=host, port=port, db=0)