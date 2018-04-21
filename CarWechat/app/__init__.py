# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
import flask_login

db = SQLAlchemy()
admin = Admin()
login_manager = flask_login.LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('localConfig.py')


    db.init_app(app)
    db.app = app

    admin.init_app(app)
    admin.app = app

    login_manager.init_app(app)

    from models.dbORM import Customer

    @login_manager.user_loader
    def user_loader(id):
        return Customer.query.filter_by(id=int(id)).first()
    # 注册蓝本
    from views import Web,Api

    app.register_blueprint(Web.web, url_prefix='/wx')
    app.register_blueprint(Api.api, url_prefix='/wx/api')

    @app.template_filter('cutstring')
    def reverse_filter(s):
        return u'%s******%s' % (s[0:4], s[-4:])
    # 附加路由和自定义的错误页面

    return app