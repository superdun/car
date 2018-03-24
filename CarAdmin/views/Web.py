# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template,current_app
from flask_login import login_required
from db.dbORM import *
from modules.CarSDK import CarOlineApi

web = Blueprint('web', __name__)
QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')
account = current_app.config.get('CAR_ACCOUNT', '')
password = current_app.config.get('CAR_PASSWORD', '')
carApi = CarOlineApi(account=account, password=password)

@web.route('/')
@login_required
def carIndex():
    return render_template('car/index.html', imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/car/<id>')
@login_required
def carDetail(id):
    data = Car.query.filter_by(id=int(id)).first()
    carApi.getToken()
    car = Car.query.get(id)
    print car.Gps.code
    GPSData={}
    rawGPSData = carApi.tracking(car.Gps.code)
    if rawGPSData['ret']==0:
        GPSData = rawGPSData['data'][0]
        address = carApi.address(GPSData['lng'], GPSData['lat'])
        from helpers.dateHelper import getTimeFromStamp
        if address['ret'] == 0:
            GPSData['address'] = address['address']

        else:
            GPSData['address'] = u'获取地理位置失败'
        GPSData['updateTime'] = getTimeFromStamp(GPSData["gps_time"])
        if GPSData['device_info'] == 0:
            GPSData['GPSStatus'] = u'正常'
        elif GPSData['device_info'] == 1:
            GPSData['GPSStatus'] = u'未上线'
        elif GPSData['device_info'] == 2:
            GPSData['GPSStatus'] = u'过期'
        elif GPSData['device_info'] == 3:
            GPSData['GPSStatus'] = u'离线'
    else:
        GPSData['address'] = u'获取地理位置失败'
        GPSData['updateTime'] = u'获取更新时间失败'
        GPSData['GPSStatus'] = u'获取设备状态失败'
    return render_template('car/carDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN,GPSData=GPSData)


@web.route('/car')
@login_required
def carList():
    data = Car.query.all()
    return render_template('car/carList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/history/<id>')
@login_required
def historyDetail(id):
    data = History.query.filter_by(id=int(id)).first()
    return render_template('car/historyDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/history')
@login_required
def historyList():
    data = History.query.all()
    return render_template('car/historyList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/mendHistory/<id>')
@login_required
def mendHistoryDetail(id):
    data = Mendhistory.query.filter_by(id=int(id)).first()
    return render_template('car/mendHistoryDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/mendHistory')
@login_required
def mendHistoryList():
    data = Mendhistory.query.all()
    return render_template('car/mendHistoryList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/customer/<id>')
@login_required
def customerDetail(id):
    data = Customer.query.filter_by(id=int(id)).first()
    return render_template('car/customerDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/customer')
@login_required
def customerList():
    data = Customer.query.all()
    return render_template('car/customerList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/carRec/<id>')
@login_required
def carRec(id):
    data = Car.query.filter_by(id=int(id)).first()

    return render_template('car/carRec.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)
