from flask import current_app
import redis

def redis_client():
    host = current_app.config.get("REDIS_HOST")
    port = current_app.config.get("REDIS_PORT")
    return redis.StrictRedis(host=host, port=port, db=0)