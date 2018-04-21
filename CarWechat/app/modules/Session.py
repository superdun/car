from wechatpy.session.redisstorage import RedisStorage
import Redis
def session_interface():
    return  RedisStorage(
        Redis.redis_client(),
        prefix="wechatpy"
    )
