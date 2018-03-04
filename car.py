# -*- coding:utf-8 -*-
from dbORM import *
from flask import render_template,jsonify,url_for,request
from test import CarOlineApi
from moduleGlobal import API_PREFIX
import flask_restless
import requests
# from moduleLogin import *

apiManager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)


# def check_sign_up(data=None, **kw):
#     sign_up_valid(data)


@app.route('/')
def hello_world():
    return 'Hello World!!!'
@app.route('/api/carrec/<imei>')
def carRecApi(imei):
    account = app.config.get('CAR_ACCOUNT', '')
    password = app.config.get('CAR_PASSWORD', '')
    carApi = CarOlineApi(account=account,password=password)
    carApi.getToken()
    data = carApi.history(imei,int(time.time()-3600*48),int(time.time()-3600*24))
    carId = Gps.query.filter_by(code=imei).first().cars[0].id
    carName = Gps.query.filter_by(code=imei).first().cars[0].name
    carImg = Gps.query.filter_by(code=imei).first().cars[0].img
    print data
    if data['msg']=='OK':
        for i in  data['data']:

            i['car'] = {'id':carId,'name':carName,'img':carImg}
            # address = carApi.address(i['lng'],i['lat'])
            # if address['ret']==0:
            #     i['address'] = address['address']
            # else:
            #     i['address'] = u'获取地理位置失败'
        return jsonify({'status':'ok','msg':data['msg'],'data':data['data']})
    else:
        return jsonify({'status': 'error', 'msg': data['msg'], 'data': []})
@app.route('/api/carmonitor')
def carMonitorApi():
    account = app.config.get('CAR_ACCOUNT', '')
    password = app.config.get('CAR_PASSWORD', '')
    carApi = CarOlineApi(account=account,password=password)
    carApi.getToken()
    data = carApi.monitor()
    print data
    if data['msg']=='OK':
        for i in  data['data']:
            carId = Gps.query.filter_by(code=i['imei']).first().cars[0].id
            carName = Gps.query.filter_by(code=i['imei']).first().cars[0].name
            carImg = Gps.query.filter_by(code=i['imei']).first().cars[0].img
            i['car'] = {'id':carId,'name':carName,'img':carImg}
            address = carApi.address(i['lng'],i['lat'])
            if address['ret']==0:
                i['address'] = address['address']
            else:
                i['address'] = u'获取地理位置失败'
        return jsonify({'status':'ok','msg':data['msg'],'data':data['data']})
    else:
        return jsonify({'status': 'error', 'msg': data['msg'], 'data': []})
@app.route('/carIndex')
def carIndex():
    return render_template('car/index.html')
@app.route('/carDetail/<id>')
def carDetail(id):
    data = Car.query.filter_by(id=int(id)).first()
    return render_template('car/carDetail.html',data=data)
@app.route('/historyDetail/<id>')
def historyDetail(id):
    data = History.query.filter_by(id=int(id)).first()
    return render_template('car/historyDetail.html',data=data)
@app.route('/mendHistoryDetail/<id>')
def mendHistoryDetail(id):
    data = Mendhistory.query.filter_by(id=int(id)).first()
    return render_template('car/mendHistoryDetail.html',data=data)
@app.route('/customerDetail/<id>')
def customerDetail(id):
    data = Customer.query.filter_by(id=int(id)).first()
    return render_template('car/customerDetail.html',data=data)
@app.route('/carRec/<id>')
def carRec(id):
    data  = Gps.query.filter_by(id=int(id)).first()

    return render_template('car/carRec.html',data=data)
#APIS

# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,preprocessors = {"POST":[check_sign_up],"GET_MANY":[get_user_list],},exclude_columns=["password"])
# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,exclude_columns=["password"])
#
apiManager.create_api(Car, methods=['GET','POST','PATCH'])
apiManager.create_api(Gps, methods=['GET','POST','PATCH'])
apiManager.create_api(History, methods=['GET','POST','PATCH'])
apiManager.create_api(Customer, methods=['GET','POST','PATCH'])
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
if __name__ == '__main__':
    app.run()
