# -*- coding:utf-8 -*-
from dbORM import *
from flask import render_template, jsonify, url_for, request, redirect
import hashlib
from test import CarOlineApi
from moduleGlobal import API_PREFIX, QINIU_DOMAIN, login_manager
import moduleAdmin as admin
import flask_restless
import flask_login
from flask_login import login_required

# from moduleLogin import *

apiManager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)


# def check_sign_up(data=None, **kw):
#     sign_up_valid(data)


# @app.route('/')
# def hello_world():
#     return 'Hello World!!!'
@app.route('/api/carrec/<imei>')
def carRecApi(imei):
    started_at = request.args.get("started_at")
    ended_at = request.args.get("ended_at")
    if not started_at or not ended_at:
        return jsonify({'status': 'error', 'msg': '时间错误', 'data': []})
    if not started_at.isdigit() or not ended_at.isdigit():
        return jsonify({'status': 'error', 'msg': '时间错误', 'data': []})
    account = app.config.get('CAR_ACCOUNT', '')
    password = app.config.get('CAR_PASSWORD', '')
    carApi = CarOlineApi(account=account, password=password)
    carApi.getToken()
    data = carApi.history(imei, int(started_at), int(ended_at))
    carId = Gps.query.filter_by(code=imei).first().cars[0].id
    carName = Gps.query.filter_by(code=imei).first().cars[0].name
    carImg = Gps.query.filter_by(code=imei).first().cars[0].img
    # print data
    if data['msg'] == 'OK':
        for i in data['data']:
            i['car'] = {'id': carId, 'name': carName, 'img': carImg}
            # address = carApi.address(i['lng'],i['lat'])
            # if address['ret']==0:
            #     i['address'] = address['address']
            # else:
            #     i['address'] = u'获取地理位置失败'
        return jsonify({'status': 'ok', 'msg': data['msg'], 'data': data['data']})
    else:
        return jsonify({'status': 'error', 'msg': data['msg'], 'data': []})


@app.route('/api/carmonitor')
def carMonitorApi():
    account = app.config.get('CAR_ACCOUNT', '')
    password = app.config.get('CAR_PASSWORD', '')
    carApi = CarOlineApi(account=account, password=password)
    carApi.getToken()
    data = carApi.monitor()
    print data
    if 'err' in data:
        return jsonify({'status': 'error', 'msg': data['err'], 'data': []})
    if data['msg'] == 'OK':
        for i in data['data']:
            carObj = Gps.query.filter_by(code=i['imei']).first()
            if carObj and carObj.cars:
                try:
                    carId = carObj.cars[0].id
                    carName = carObj.cars[0].name
                    carImg = carObj.cars[0].img
                except:
                    carId = ""
                    carName = ""
                    carImg = ""
            else:
                carId = ""
                carName = ""
                carImg = ""
            i['car'] = {'id': carId, 'name': carName, 'img': carImg}
            address = carApi.address(i['lng'], i['lat'])
            if address['ret'] == 0:
                i['address'] = address['address']
            else:
                i['address'] = u'获取地理位置失败'
        return jsonify({'status': 'ok', 'msg': data['msg'], 'data': data['data']})
    else:
        return jsonify({'status': 'error', 'msg': data['msg'], 'data': []})



@app.route('/')
@login_required
def carIndex():
    return render_template('car/index.html', imgDomain="http://%s" % QINIU_DOMAIN)


@app.route('/car/<id>')

@login_required
def carDetail(id):
    data = Car.query.filter_by(id=int(id)).first()
    return render_template('car/carDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/car')
@login_required
def carList():
    data = Car.query.all()
    return render_template('car/carList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/history/<id>')
@login_required
def historyDetail(id):
    data = History.query.filter_by(id=int(id)).first()
    return render_template('car/historyDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/history')
@login_required
def historyList():
    data = History.query.all()
    return render_template('car/historyList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/mendHistory/<id>')
@login_required
def mendHistoryDetail(id):
    data = Mendhistory.query.filter_by(id=int(id)).first()
    return render_template('car/mendHistoryDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/mendHistory')
@login_required
def mendHistoryList():
    data = Mendhistory.query.all()
    return render_template('car/mendHistoryList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/customer/<id>')
@login_required
def customerDetail(id):
    data = Customer.query.filter_by(id=int(id)).first()
    return render_template('car/customerDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/customer')
@login_required
def customerList():
    data = Customer.query.all()
    return render_template('car/customerList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)



@app.route('/carRec/<id>')
@login_required
def carRec(id):
    data = Car.query.filter_by(id=int(id)).first()

    return render_template('car/carRec.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


# APIS

# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,preprocessors = {"POST":[check_sign_up],"GET_MANY":[get_user_list],},exclude_columns=["password"])
# apiManager.create_api(User, methods=['GET',"POST"],url_prefix=API_PREFIX,exclude_columns=["password"])
#
apiManager.create_api(Car, methods=['GET', 'POST', 'PATCH'])
apiManager.create_api(Gps, methods=['GET', 'POST', 'PATCH'])
apiManager.create_api(History, methods=['GET', 'POST', 'PATCH'])
apiManager.create_api(Customer, methods=['GET', 'POST', 'PATCH'])
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
# admin
admin.dashboard()

# login



users = {}
raw_users = User.query.all()
for user in raw_users:
    users[user.name] = {'password': user.password}


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template("login.html")


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form[
                                'password'] == users[username]['password']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('/admin')
        return render_template('login.html')

    username = request.form['username']
    if username not in users:
        return 'wrong username'
    md5 = hashlib.md5()
    if request.form['password'] == "":
        return render_template('login.html')
    md5.update(request.form['password'])
    psswd = md5.hexdigest()
    if psswd == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('protected'))

    return render_template('login.html')


@app.route('/protected')
@flask_login.login_required
def protected():
    return redirect('/')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')


application = app
if __name__ == '__main__':
    app.run()
