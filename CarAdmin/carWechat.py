# -*- coding:utf-8 -*-
from flask import Flask,g
# import redis
# from flask_cache import Cache


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('localConfig.py')


API_PREFIX = app.config.get('API_PREFIX')
SECRET_KEY = app.config.get("SECRET_KEY")

with app.app_context():
    # cache = Cache(app,config={'CACHE_TYPE': 'simple',"CACHE_REDIS_HOST":app.config.get("REDIS_HOST"),"CACHE_REDIS_PORT":app.config.get("REDIS_PORT")})
    from views import *

    app.register_blueprint(Api.api, url_prefix='')

    app.register_blueprint(Web.web, url_prefix='')
    app.register_blueprint(Login.login_bp, url_prefix='')
    app.register_blueprint(WechatView.wechatView, url_prefix='/wx')
    app.register_blueprint(WechatApi.wechatapi, url_prefix='/wx/api')
    # admin

    from modules import Admin

    Admin.dashboard()

application = app
if __name__ == '__main__':
    app.run()