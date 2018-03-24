# -*- coding:utf-8 -*-
from  flask import Blueprint, jsonify, request, current_app
from db.dbORM import *
from sqlalchemy import exc
from modules.CarSDK import CarOlineApi
import hashlib
import flask_login
api = Blueprint('api', __name__)


@api.route('/idcode', methods=['POST'])
def idcodeApi():
    from modules.VCode import makeIdCode
    num = str(int(request.form['phone']))
    idCode = makeIdCode(num)
    msg = u'{"code": "%s"}' % idCode
    from modules.SMS import sendSMS
    sendResult = sendSMS('id', num, msg).send()
    print sendResult
    return jsonify({'status': 'ok', 'msg': sendResult})

@api.route('/sign', methods=['POST'])
def profileApi():

    filter_list = []
    for i in request.form:
        if request.form[i] == '' or request.form[i] == 'null':
            filter_list.append(i)
        elif len(request.form['password'])<6:
            filter_list.append("password")
        elif len(request.form['idCode'])!=18:
            filter_list.append("idCode")


    name = request.form['name']
    if request.form['driveage'].isnumeric():
        driveage = int(request.form['driveage'])
    else:
        filter_list.append("driveage")
    phone = request.form['phone']

    idCode = request.form['idCode']

    md5 = hashlib.md5()
    md5.update(request.form['password'])
    psswd = md5.hexdigest()

    vCode = str(request.form['vCode'])
    if filter_list:
        return jsonify({'status': 'lacked', 'msg': filter_list})
    from modules.VCode import cache
    if vCode != cache.get(phone):
        return jsonify({'status': 'wrongcode', 'msg': '验证码错误'})
    if flask_login.current_user.is_authenticated :
        customer = Customer.query.filter_by(openid=flask_login.current_user.openid).first()
        if customer:
            customer.name = name
            customer.phone = phone
            customer.password = psswd
            customer.driveage = driveage
            customer.idcode = idCode
        else:
            customer = Customer(name=name, phone=phone, password=psswd, driveage=driveage, idcode=idCode,status='normal')
    else:
        customer = Customer(name=name,phone=phone,password=psswd,driveage=driveage,idcode=idCode,status='normal')
    try:
        db.session.add(customer)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        if flask_login.current_user.is_authenticated:
            c = Customer.query.filter_by(openid=flask_login.current_user.openid).first()
            cu = Customer.query.filter(Customer.phone == phone or Customer.idcode == idCode).first()
            if c and not cu:
                db.session.delete(c)
                cu = Customer.query.filter(Customer.phone == phone or Customer.idcode == idCode).first()
                cu.openid = flask_login.current_user.openid
                cu.img = flask_login.current_user.img
                cu.status = 'normal'
                db.session.add(cu)
                db.session.commit()
            else:
                return jsonify({'status': 'nochange', 'msg': ""})
        else:
            return jsonify({'status': 'dup', 'msg': ""})
    cache.delete(phone)
    return jsonify({'status': 'ok', 'msg': ""})


