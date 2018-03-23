from flask import current_app
import random
from werkzeug.contrib.cache import FileSystemCache

cache =  FileSystemCache('./cache')
def makeIdCode(key):
    v = str(random.randint(100000, 999999))
    cache.set(key=key, value=v, timeout=int(current_app.config.get('VCODE_TIMEOUT')))
    return v