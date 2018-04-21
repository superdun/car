from flask import current_app
import random
import Cache

def makeIdCode(key):
    v = str(random.randint(100000, 999999))
    Cache.cache().set(key=key, value=v, timeout=int(current_app.config.get('VCODE_TIMEOUT')))
    return v