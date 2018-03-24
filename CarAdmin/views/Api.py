# -*- coding:utf-8 -*-
from  flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from db.dbORM import *
from modules.CarSDK import CarOlineApi

api = Blueprint('api', __name__)
account = current_app.config.get('CAR_ACCOUNT', '')
password = current_app.config.get('CAR_PASSWORD', '')
carApi = CarOlineApi(account=account, password=password)

@api.route('/api/carrec/<imei>')
def carRecApi(imei):
    started_at = request.args.get("started_at")
    ended_at = request.args.get("ended_at")
    if not started_at or not ended_at:
        return jsonify({'status': 'error', 'msg': '时间错误', 'data': []})
    if not started_at.isdigit() or not ended_at.isdigit():
        return jsonify({'status': 'error', 'msg': '时间错误', 'data': []})
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


@api.route('/api/carmonitor')
def carMonitorApi():

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
@api.route('/api/carmonitor/<id>')
def oneCarMonitorApi(id):
    carApi.getToken()
    car = Car.query.get(id)
    data = carApi.tracking(car.imei)
    return jsonify(data)