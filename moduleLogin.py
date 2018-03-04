# -*- coding:utf-8 -*-
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import flask_restless
from moduleGlobal import SECRET_KEY,cache
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from dbORM import User
from moduleGlobal import app

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if not user :
        user = User.query.filter_by(email=username).first()
    if not user :
        user = User.query.filter_by(mobile=username).first()
    if user and verify_password( str(password),user.password):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()

jwt = JWT(app, authenticate, identity)


@jwt_required()
def post_create_auth_func(**kw):
    kw["data"]["user_id"] = current_identity.id
@jwt_required()
def post_patch_many_auth_func(**kw):
    if not current_identity.auth != 0:
        raise flask_restless.ProcessingException(description='Not authenticated!', code=401)
@jwt_required()
def post_patch_auth_func(**kw):
    if not current_identity.id != kw["data"]["user_id"]:
        raise flask_restless.ProcessingException(description='Not authenticated!', code=401)
    kw["data"]["updated_at"] = datetime.utcnow()

@jwt_required()
def user_auth_func(**kw):
    if not current_identity.id != kw["data"]["user_id"]:
        raise flask_restless.ProcessingException(description='Not authenticated!', code=401)

@jwt_required()
def get_user_list(**kw):
    if  current_identity.auth != 0:
        raise flask_restless.ProcessingException(description='Not authenticated!', code=401)




def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password( password,password_in_db):
    return pwd_context.verify(password, password_in_db)

def sign_up_valid(form):
    if not (form.get("username", None) or form.get("mobile", None) or form.get("email", None)):

        raise flask_restless.ProcessingException(description=u'用户名/手机/电子邮件 错误', code=400)
    elif not form.get("password", None):
        raise flask_restless.ProcessingException(description=u'密码 错误', code=400)
    else:
        form["password"] = hash_password(form.get("password", None))
