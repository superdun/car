# -*- coding:utf-8 -*-
import os, sys
from  flask import Blueprint, request, current_app, url_for, jsonify
from ..models.dbORM import *
from sqlalchemy import exc
from ..modules.CarSDK import CarOlineApi
import hashlib
import flask_login
from ..modules import Wechat as wx
from wechatpy.exceptions import (
    InvalidSignatureException,
    WeChatPayException
)
from datetime import datetime
from wechatpy.utils import timezone
import time
import json
import random
from ..modules.Preferential import getFees
from ..modules.Limit import checkLimit
from app import db

api = Blueprint('api', __name__)


def getOutTradeNo():
    now = datetime.fromtimestamp(time.time(), tz=timezone('Asia/Shanghai'))
    return '{0}{1}{2}'.format(
        current_app.config.get("WECHAT_MCH_ID"),
        now.strftime('%Y%m%d%H%M%S'),
        random.randint(1000, 10000)
    )


@api.route('/idcode', methods=['POST'])
def idcodeApi():
    from ..modules.VCode import makeIdCode
    num = str(int(request.form['phone']))
    idCode = makeIdCode(num)
    msg = '{"code": "%s"}' % idCode
    from ..modules.SMS import sendSMS
    sendResult = sendSMS('id', num, msg.decode('utf8')).send()
    print sendResult
    return jsonify({'status': 'ok', 'msg': sendResult})


@api.route('/sign', methods=['POST'])
def profileApi():
    filter_list = []
    for i in request.form:
        if request.form[i] == '' or request.form[i] == 'null':
            filter_list.append(i)
        # elif len(request.form['password']) < 6:
        #     filter_list.append("password")
        elif len(request.form['idCode']) != 18:
            filter_list.append("idCode")
        elif len(request.form['name']) == 0:
            filter_list.append("name")
    name = request.form['name']
    if request.form['driveage'].isnumeric():
        driveage = int(request.form['driveage'])
    else:
        filter_list.append("driveage")
    phone = request.form['phone']

    idCode = request.form['idCode']

    # md5 = hashlib.md5()
    # md5.update(request.form['password'])
    # psswd = md5.hexdigest()

    vCode = str(request.form['vCode'])
    if filter_list:
        return jsonify({'status': 'lacked', 'msg': filter_list})
    from ..modules.VCode import Cache
    if vCode != Cache.cache().get(phone):
        return jsonify({'status': 'alert', 'msg': '验证码错误'})
    from ..modules.VerifyIdcard import Verify
    idCodeVerifyResult = Verify(idCode, name)
    if idCodeVerifyResult['status'] == 'failed':
        return jsonify({'status': 'alert', 'msg': '身份证验证服务器出错，请稍后重试'})
    elif not idCodeVerifyResult['isok']:
        return jsonify({'status': 'alert', 'msg': '身份证姓名不匹配'})
    if flask_login.current_user.is_authenticated:
        customer = Customer.query.filter_by(openid=flask_login.current_user.openid).first()
        if customer:
            customer.name = name
            customer.phone = phone
            # customer.password = psswd
            customer.driveage = driveage
            customer.idcode = idCode
            customer.status = 'normal'
        else:
            customer = Customer(name=name, phone=phone, driveage=driveage, idcode=idCode,
                                status='normal', created_at=datetime.now())
    else:
        customer = Customer(name=name, phone=phone, driveage=driveage, idcode=idCode, status='normal',
                            created_at=datetime.now())
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
                return jsonify({'status': 'alert', 'msg': "您已经注册过，不能修改信息，如有疑问请联系客服人工修改"})
        else:
            return jsonify({'status': 'alert', 'msg': "当前手机号码/身份证号已存在"})
    Cache.cache().delete(phone)
    return jsonify({'status': 'ok', 'msg': ""})


@api.route('/getpayresult', methods=["POST"])
def getPayResult():
    wxPay = wx.getPay()
    if wxPay.sandbox:
        sandKey = wxPay._fetch_sanbox_api_key()
        wxPay.sandbox_api_key = sandKey
    try:
        r = wxPay.parse_payment_result(request.data)
    except InvalidSignatureException, e:
        e = Error(msg=e.errmsg, type=3)
        db.session.add(e)
        db.session.commit()
        return
    order = Order.query.filter_by(tradeno=r["out_trade_no"]).first()
    if r["return_code"] == "SUCCESS":

        if not order:
            e = Error(msg=json.dumps(r), type=1)
            db.session.add(e)
            db.session.commit()
        else:
            if not order.wxtradeno:
                order.wxtradeno = r["transaction_id"]
                order.pay_at = r["time_end"]
                order.status = "ok"
                order.Customer.olduser = 1
                db.session.add(order)
                db.session.commit()
                wx.sendTemplateByOrder(order, u"通力新订单通知", u"在线下单")

    else:
        rr = wxPay.close(r["out_trade_no"])
        order.status = "failed"
        order.detail = r["err_code_des"]
        db.session.add(order)
        db.session.commit()
    return "ok"


@api.route('/makeorder', methods=['POST'])
@flask_login.login_required
def getOrderApi():
    carTypeId = request.form.get("id")
    count = request.form.get("count")



    location = request.form.get("location")
    serverstop = request.form.get("serverstop")
    insureid = request.form.get("insureid")
    book_at = request.form.get("book_at")

    insure = Insure.query.filter_by(id=insureid).first()

    if serverstop:
        serverstop = int(serverstop)
    else:
        serverstop = None
    import datetime as dt
    from ..modules.Limit import dateCounvert
    # book_at = "2018-05-27T08:30:45"
    if not book_at:
        book_at = ""
    else:
        try:
            if dateCounvert(book_at)<datetime.now()-dt.timedelta(hours=1):
                return jsonify({'status': 'error', 'code': 7, 'msg': "预约时间有误"})
        except :
            return jsonify({'status': 'error', 'code': 7, 'msg': "预约时间有误"})

    checkResult = checkLimit(carTypeId, count, book_at)
    if checkResult["limit"]:
        return  jsonify({'status': 'error', 'code': 6, 'msg': checkResult['msg']})
    if (not carTypeId) or (not count):
        return jsonify({'status': 'error', 'code': 1, 'msg': "参数错误"})
    car = Cartype.query.filter_by(id=int(carTypeId)).first()
    if not car:
        return jsonify({'status': 'error', 'code': 2, 'msg': "未找到商品"})
    if int(count) < 0:
        return jsonify({'status': 'error', 'code': 3, 'msg': "数量错误"})
    if not flask_login.current_user.is_authenticated:
        return jsonify({'status': 'error', 'code': 4, 'msg': "登陆错误"})
    if car.count == 0:
        return jsonify({'status': 'error', 'code': 5, 'msg': "此车已经订完，请选择其他车辆"})
    carName = car.name
    body = u"%s*%s天" % (carName, count)
    carfee = int(car.price) * int(count)
    oldfee = carfee
    cutfee = 0
    open_id = flask_login.current_user.openid
    prefer = getFees(carTypeId, count, carfee,open_id,book_at)
    preferentialid = None
    if prefer['isprefer']:
        carfee = prefer['newfee']
        cutfee = prefer['cutfee']
        oldfee = prefer['oldfee']
        preferentialid = prefer['preferid']

    if insure:
        ins_id = insureid
        insurefee = int(insure.price) * int(count)
    else:
        ins_id = None
        insurefee = 0
    totalfee = carfee + insurefee
    notify_url = current_app.config.get('WECHAT_HOST') + url_for('api.getPayResult')


    order = Order(created_at=datetime.now(), customeropenid=open_id, carid=int(carTypeId), totalfee=totalfee,
                  tradetype='JSAPI', count=int(count), oldfee=oldfee, cutfee=cutfee, preferentialdetail=json.dumps(prefer),
                  location=location, serverstopid=serverstop, carfee=carfee, insurefee=insurefee, insureid=ins_id,
                  book_at=book_at)

    wxPay = wx.getPay()
    out_trade_no = getOutTradeNo()
    try:
        oresult = wxPay.order.create(trade_type='JSAPI', body=body, total_fee=totalfee, notify_url=notify_url,
                                     user_id=open_id, out_trade_no=out_trade_no, )

    except WeChatPayException, e:
        e = Error(msg=e.errmsg, type=4)
        # models.session.add(order)
        db.session.add(e)
        db.session.commit()
        return jsonify({'status': 'failed', 'orderId': order.id, 'msg': u"订单创建失败"})
    if oresult['return_code'] == 'SUCCESS':
        prepay_id = oresult['prepay_id']
        order.prepayid = prepay_id
        order.tradeno = out_trade_no
        order.status = 'waiting'
        order.detail = json.dumps(wxPay.jsapi.get_jsapi_params(prepay_id))
        car.count = car.count - 1
        db.session.add(order)
        db.session.add(car)
        db.session.commit()
        return jsonify({'status': 'ok', 'orderId': order.id, 'result': wxPay.jsapi.get_jsapi_params(prepay_id)})
    else:
        order.status = 'failed'
        order.tradeno = out_trade_no
        db.session.add(order)
        db.session.commit()
        return jsonify({'status': 'failed', 'orderId': order.id, 'result': oresult["err_code_des"]})


@api.route('/cancelorder/<id>')
@flask_login.login_required
def cancelOrderApi(id):
    wxPay = wx.getPay()
    if wxPay.sandbox:
        sandKey = wxPay._fetch_sanbox_api_key()
        wxPay.sandbox_api_key = sandKey
    order = Order.query.filter_by(id=id).first()
    if not order:
        return jsonify({"status": 'ok'})
    tradeNo = order.tradeno
    rr = wxPay.order.close(tradeNo)
    if rr['result_code'] == "SUCCESS":
        order.status = "canceled"
        order.detail = json.dumps(rr)
        order.Cartype.count = order.Cartype.count + 1
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": 'ok'})
    else:
        return jsonify({"status": 'failed'})
        # try:
        #     wxPay = wx.getPay()
        #     if wxPay.sandbox:
        #         sandKey = wxPay._fetch_sanbox_api_key()
        #         wxPay.sandbox_api_key = sandKey
        #     order = Order.query.filter_by(id=id).first()
        #     if not order:
        #         return jsonify({"status": 'ok'})
        #     tradeNo = order.tradeno
        #     rr = wxPay.close(tradeNo)
        #     order.status = "canceled"
        #     order.detail = json.dumps(rr)
        #     models.session.add(order)
        #
        #     models.session.commit()
        # except:
        #     return jsonify({"status": 'failed'})
        # return jsonify({"status": 'ok'})


@api.route('/refundapply/<id>')
@flask_login.login_required
def refundApplyApi(id):
    order = Order.query.filter_by(id=id).first()
    order.status = 'refunding'
    order.isrefund = 1
    db.session.add(order)
    db.session.commit()
    wx.sendTemplateByOrder(order, u"通力退款通知", u"在线退款")

    return jsonify({"status": 'ok'})


@api.route('/preferential', methods=['POST'])
@flask_login.login_required
def getPreferential():
    carTypeId = request.form.get("id")
    count = request.form.get("count")
    book_at = request.form.get("book_at")
    # book_at = "2018-05-27T08:30:45"
    if not book_at:
        book_at = ""
    if (not carTypeId) or (not count):
        return jsonify({'status': 'error', 'code': 1, 'msg': "参数错误"})
    car = Cartype.query.filter_by(id=int(carTypeId)).first()
    if not car:
        return jsonify({'status': 'error', 'code': 2, 'msg': "未找到商品"})
    if int(count) < 0:
        return jsonify({'status': 'error', 'code': 3, 'msg': "数量错误"})
    if not flask_login.current_user.is_authenticated:
        return jsonify({'status': 'error', 'code': 4, 'msg': "登陆错误"})
    openid = flask_login.current_user.openid
    totalfee = int(car.price) * int(count)
    prefer = getFees(carTypeId, count, totalfee,openid,book_at)
    return jsonify(prefer)


@api.route('/serverstop')
@flask_login.login_required
def getserverstop():
    r = {'status': 'ok', "data": []}
    serverstop = Serverstop.query.all()
    for i in serverstop:
        r['data'].append({'name': i.name, 'phone': i.phone, 'owner': i.owner, 'lat': i.lat, 'lng': i.lng})
    return jsonify(r)


@api.route('/getrecount')
@flask_login.login_required
def getrecount():
    carTypeId = request.args.get("id")
    car = Cartype.query.filter_by(id=int(carTypeId)).first()
    if car.count == 0:
        return jsonify({'status': 'failed'})
    return jsonify({'status': 'ok'})
