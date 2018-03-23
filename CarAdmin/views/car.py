# # -*- coding:utf-8 -*-
# import hashlib
#
# import flask_login
# import flask_restless
# from flask import render_template, jsonify, url_for, request, redirect
#
# from db.dbORM import *
# from modules import Admin as admin
# from modules.CarSDK import CarOlineApi
# from modules.Global import login_manager

# from moduleLogin import *

# apiManager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)


# def check_sign_up(data=None, **kw):
#     sign_up_valid(data)


# @app.route('/')
# def hello_world():
#     return 'Hello World!!!'




# APIS

# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,preprocessors = {"POST":[check_sign_up],"GET_MANY":[get_user_list],},exclude_columns=["password"])
# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,exclude_columns=["password"])
#
# apiManager.create_api(Car, methods=['GET', 'POST', 'PATCH'])
# apiManager.create_api(Gps, methods=['GET', 'POST', 'PATCH'])
# apiManager.create_api(History, methods=['GET', 'POST', 'PATCH'])
# apiManager.create_api(Customer, methods=['GET', 'POST', 'PATCH'])
# apiManager.create_api(Question, methods=['GET','POST','PATCH'],url_prefix=API_PREFIX,preprocessors = {"POST":[post_create_auth_func],"PATCH_SINGLE":[post_patch_auth_func],"PATCH_MANY":[post_patch_many_auth_func]},exclude_columns=["User.password"])
# apiManager.create_api(Project, methods=['GET','POST','PATCH'],url_prefix=API_PREFIX,preprocessors = {"POST":[post_create_auth_func],"PATCH_SINGLE":[post_patch_auth_func],"PATCH_MANY":[post_patch_many_auth_func]},exclude_columns=["User.password"])
# apiManager.create_api(PostComment, methods=['GET','POST','PATCH'],url_prefix=API_PREFIX,preprocessors = {"POST":[post_create_auth_func],"PATCH_SINGLE":[post_patch_auth_func],"PATCH_MANY":[post_patch_many_auth_func]},exclude_columns=["User.password"])
# apiManager.create_api(QuestionComment, methods=['GET','POST','PATCH'],url_prefix=API_PREFIX,preprocessors = {"POST":[post_create_auth_func],"PATCH_SINGLE":[post_patch_auth_func],"PATCH_MANY":[post_patch_many_auth_func]},exclude_columns=["User.password"])
# apiManager.create_api(ProjectComment, methods=['GET','POST','PATCH'],url_prefix=API_PREFIX,preprocessors = {"POST":[post_create_auth_func],"PATCH_SINGLE":[post_patch_auth_func],"PATCH_MANY":[post_patch_many_auth_func]},exclude_columns=["User.password"])
#
# apiManager.create_api(Field, methods=['GET'],url_prefix=API_PREFIX)
# apiManager.create_api(PostTag, methods=['GET'],url_prefix=API_PREFIX)
# apiManager.create_api(ProjectTag, methods=['GET'],url_prefix=API_PREFIX)
# apiManager.create_api(QuestionTag, methods=['GET'],url_prefix=API_PREFIX)
# apiManager.create_api(Notification, methods=['GET','POST'],url_prefix=API_PREFIX,exclude_columns=["from.password","to.password"])
# apiManager.create_api(Message, methods=['GET','POST'],url_prefix=API_PREFIX,exclude_columns=["from.password","to.password"])






