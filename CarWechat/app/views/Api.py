# -*- coding:utf-8 -*-
import os, sys
from  flask import Blueprint, request, current_app, url_for, jsonify
from ..models.dbORM import *
from sqlalchemy import exc
from ..modules.CarSDK import CarOlineApi
import hashlib
from ..helpers.GetAllRealteOrders import getOrderSumData
import flask_login
from ..modules import Wechat as wx
from wechatpy.exceptions import (
    InvalidSignatureException,
    WeChatPayException
)
from ..modules.Integral import *
import datetime as dt
from datetime import datetime as dtt
from wechatpy.utils import timezone
import time
import json
import random
from ..modules.Preferential import getFees
from ..modules.Limit import checkLimit

from app import db

api = Blueprint('api', __name__)


def getOutTradeNo():
    now = dtt.fromtimestamp(time.time(), tz=timezone('Asia/Shanghai'))
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
        if (request.form[i] == '' or request.form[i] == 'null') and i!="referee":
            filter_list.append(i)
        # elif len(request.form['password']) < 6:
        #     filter_list.append("password")
        elif len(request.form['idCode']) != 18:
            filter_list.append("idCode")
        elif len(request.form['name']) == 0:
            filter_list.append("name")
    name = request.form['name']
    driveage = 0
    if request.form['driveage'].isnumeric():
        driveage = int(request.form['driveage'])
    else:
        filter_list.append("driveage")
    phone = request.form['phone']

    idCode = request.form['idCode']
    referee = request.form['referee']
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

    signIntegral = 0
    if referee:
        refereeCustomer = Customer.query.filter_by(phone=referee).first()

        if refereeCustomer:
            admin = User.query.filter_by(openid=refereeCustomer.openid).first()
            if admin:
                return jsonify({'status': 'alert', 'msg': '推荐人不能为代理'})
        else:
            return jsonify({'status': 'alert', 'msg': '推荐人不存在，请检查'})

    if flask_login.current_user.is_authenticated:
        customer = Customer.query.filter_by(openid=flask_login.current_user.openid).first()
        if customer:
            customer.name = name
            customer.phone = phone
            # customer.password = psswd
            customer.refereephone = referee
            customer.driveage = driveage
            customer.idcode = idCode
            customer.status = 'nopay'
        else:
            customer = Customer(name=name, phone=phone, driveage=driveage, idcode=idCode,
                                status='nopay', created_at=dtt.now(), refereephone=referee)
    else:
        return jsonify({'status': 'alert', 'msg': "请使用微信自带浏览器注册或十分钟后重试"})
        # customer = Customer(name=name, phone=phone, driveage=driveage, idcode=idCode, status='nopay',
        #                     created_at=dtt.now(), refereephone = referee)
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
                cu.status = 'nopay'
                cu.refereephone = referee
                db.session.add(cu)
                db.session.commit()
            else:
                return jsonify({'status': 'alert', 'msg': "您已经注册过，不能修改信息，如有疑问请联系客服人工修改"})
        else:
            return jsonify({'status': 'alert', 'msg': "当前手机号码/身份证号已存在"})
    Cache.cache().delete(phone)
    return jsonify({'status': 'ok', 'msg': "", "openid": flask_login.current_user.openid})


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
                sourceOrderId = order.id
                if order.ordertype == "continue":
                    sourceOrder = Order.query.filter_by(id=order.sourceid).first()
                    sourceOrder.hascontinue = 1
                    db.session.add(sourceOrder)
                    sourceOrderId = sourceOrder.id
                else:
                    order.orderstatus = "start"
                cIntegral = order.Customer.integral
                integralImprove = getIntegralImprove(order.totalfee, u"积分")

                refereeCustomer = Customer.query.filter_by(phone=order.Customer.refereephone).first()
                integralRefereeImprove=0
                if refereeCustomer:
                    admin = User.query.filter_by(openid=refereeCustomer.openid).first()
                    if not admin:
                        integralRefereeImprove = getIntegralImprove(order.totalfee, u"返点")
                        refereeCustomer.integral = refereeCustomer.integral + integralRefereeImprove
                        db.session.add(refereeCustomer)
                        db.session.commit()
                integtalused = 0
                if order.integtalused:
                    integtalused = order.integtalused
                order.Customer.integral = integralImprove + cIntegral - integtalused
                db.session.add(order)
                db.session.commit()
                if integtalused:
                    saveIntegeralRecord(order.Customer,-1*int(integtalused), u"抵现", order.id)
                if integralImprove>0:
                    saveIntegeralRecord(order.Customer, integralImprove, u"积分", order.id)
                if refereeCustomer:
                    saveIntegeralRecord(refereeCustomer,integralRefereeImprove, u"返点", order.id)

                wx.sendTemplateByOrder(order, u"通力新订单通知", u"在线下单",
                                       current_app.config.get('WECHAT_HOST') + url_for("agentweb.wechatCodeOrder",
                                                                                       id=sourceOrderId))

    else:
        rr = wxPay.close(r["out_trade_no"])
        order.status = "failed"
        order.detail = r["err_code_des"]
        db.session.add(order)
        db.session.commit()
    return "ok"


def signIntegralFunc(customer,referee=None):
    signIntegral = getIntegral(u"注册")
    if referee:
        refereeCustomer = Customer.query.filter_by(phone=referee).first()
        if refereeCustomer:
            admin = User.query.filter_by(openid=refereeCustomer.openid).first()

            recomendIntegral = getIntegral(u"推荐")

            if not admin:
                refereeCustomer.integral = refereeCustomer.integral + recomendIntegral
                db.session.add(refereeCustomer)
                db.session.commit()
                saveIntegeralRecord(refereeCustomer, recomendIntegral, u"作为" + customer.name + u"的推荐人")

    customer.integral = signIntegral
    db.session.add(customer)
    db.session.commit()
    saveIntegeralRecord(customer, signIntegral, u"注册")

@api.route('/getsignpayresult', methods=["POST"])
def getSignPayResult():
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
    order = Otherorder.query.filter_by(tradeno=r["out_trade_no"]).first()
    referee = order.Customer.refereephone

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

                order.Customer.status = "normal"
                signIntegralFunc(order.Customer,referee)
                db.session.add(order)
                db.session.commit()

    else:
        rr = wxPay.close(r["out_trade_no"])
        order.status = "failed"
        order.detail = r["err_code_des"]
        db.session.add(order)
        db.session.commit()
    return "ok"



@api.route('/makesignorder', methods=['POST'])
@flask_login.login_required
def getSignOrderApi():
    ordertype = "sign"
    open_id = request.form.get("open_id")
    customer = Customer.query.filter_by(openid=open_id).filter_by(status="nopay").first()
    if not customer:
        return jsonify({'status': 'error', 'msg': u"未知错误，请联系代理"})
    integral = Integral.query.filter_by(name=u"注册费用").first()
    if not integral or integral.ration<0.01:
        customer.status = "normal"
        signIntegralFunc(customer, customer.refereephone)
        return jsonify({'status': 'noneed', 'msg': u"无需付费"})
    totalfee = int(integral.ration) * 100

    notify_url = current_app.config.get('WECHAT_HOST') + url_for('api.getSignPayResult')
    body = u"%s*%s" % (customer.name, str(totalfee))
    order = Otherorder(created_at=dtt.now(), customeropenid=open_id, totalfee=totalfee,
                       tradetype='JSAPI', ordertype=ordertype)

    wxPay = wx.getPay()
    out_trade_no = getOutTradeNo()
    try:
        oresult = wxPay.order.create(trade_type='JSAPI', body=body, total_fee=totalfee, notify_url=notify_url,
                                     user_id=open_id, out_trade_no=out_trade_no, )

    except WeChatPayException, e:
        err = Error(msg=e.errmsg, type=4)
        # models.session.add(order)
        db.session.add(err)
        db.session.commit()
        return jsonify({'status': 'failed', 'orderId': order.id, 'msg': u"订单创建失败"})
    if oresult['return_code'] == 'SUCCESS':
        prepay_id = oresult['prepay_id']
        order.prepayid = prepay_id
        order.tradeno = out_trade_no
        order.status = 'waiting'
        order.detail = json.dumps(wxPay.jsapi.get_jsapi_params(prepay_id))
        # if order.ordertype != "continue":
        # car.count = car.count - 1
        db.session.add(order)
        db.session.commit()
        return jsonify({'status': 'ok', 'orderId': order.id, 'result': wxPay.jsapi.get_jsapi_params(prepay_id)})
    else:
        order.status = 'failed'
        order.tradeno = out_trade_no
        db.session.add(order)
        db.session.commit()
        return jsonify({'status': 'failed', 'orderId': order.id, 'result': oresult["err_code_des"]})


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
    hasntegral = request.form.get("hasIntegral")
    if serverstop and serverstop.isnumeric():
        serverstop = int(serverstop)
    else:
        return jsonify({'status': 'error', 'code': 7, 'msg': "请选择最近的服务站"})
    from ..modules.Limit import dateCounvert
    # book_at = "2018-05-27T08:30:45"

    if request.form.get("iscontinue") == "true" and request.form.get("orderid").isnumeric():
        ordertype = "continue"
        sourceid = int(request.form.get("orderid"))
        sourceOrder = Order.query.filter_by(id=sourceid).first()
        sourceFromDate = sourceOrder.fromdate
        if not sourceFromDate:
            return jsonify({'status': 'error', 'code': 9, 'msg': "尚未发车，不能续租"})
        continueOrders = Order.query.filter_by(sourceid=sourceid).filter_by(status="ok").all()
        OrderSumData = getOrderSumData(sourceOrder, continueOrders)
        book_at = (sourceFromDate + datetime.timedelta(days=OrderSumData["countSum"])).strftime('%Y-%m-%dT%H:%M:%S')
    else:
        ordertype = "normal"
        sourceid = None
    if not book_at:
        book_at = dtt.now().strftime('%Y-%m-%dT%H:%M:%S')
    else:
        pass
        # try:
        #     if dateCounvert(book_at)<datetime.now()-dt.timedelta(hours=5):
        #         return jsonify({'status': 'error', 'code': 7, 'msg': "预约时间有误"})
        # except :
        #     return jsonify({'status': 'error', 'code': 7, 'msg': "预约时间有误"})

    checkResult = checkLimit(carTypeId, count, book_at)
    if checkResult["limit"]:
        return jsonify({'status': 'error', 'code': 6, 'msg': checkResult['msg']})
    if (not carTypeId) or (not count):
        return jsonify({'status': 'error', 'code': 1, 'msg': "参数错误"})
    car = Cartype.query.filter_by(id=int(carTypeId)).first()
    if not car:
        return jsonify({'status': 'error', 'code': 2, 'msg': "未找到商品"})
    if int(count) < 0:
        return jsonify({'status': 'error', 'code': 3, 'msg': "数量错误"})
    if not flask_login.current_user.is_authenticated:
        return jsonify({'status': 'error', 'code': 4, 'msg': "登陆错误"})
    if car.remind_count == 0:
        return jsonify({'status': 'error', 'code': 5, 'msg': "此车已经订完，请选择其他车辆"})
    carName = car.name
    body = u"%s*%s天" % (carName, count)
    carfee = int(car.price) * int(count)
    oldfee = carfee
    cutfee = 0
    open_id = flask_login.current_user.openid
    prefer = getFees(carTypeId, count, carfee, open_id, book_at)
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
    integralfee = 0
    integtalused = 0
    if hasntegral == 'true':
        getIntegralResult = getIntegralCut(open_id, totalfee)
        integralfee = getIntegralResult["cut"]*100
        totalfee = int(totalfee - integralfee)
        integtalused = getIntegralResult["used"]
    notify_url = current_app.config.get('WECHAT_HOST') + url_for('api.getPayResult')
    try:
        serverstopLocation = Serverstop.query.filter_by(id=serverstop).first().Location.name
    except:
        serverstopLocation = None
    order = Order(created_at=dtt.now(), customeropenid=open_id, carid=int(carTypeId), totalfee=totalfee,
                  tradetype='JSAPI', count=int(count), oldfee=oldfee, cutfee=cutfee,
                  preferentialdetail=json.dumps(prefer),
                  location=location, serverstopid=serverstop, carfee=carfee, insurefee=insurefee, insureid=ins_id,
                  book_at=book_at, ordertype=ordertype, sourceid=sourceid, integralfee=integralfee,
                  serverstoplocation=serverstopLocation, notystatus=0, integtalused=integtalused)

    wxPay = wx.getPay()
    out_trade_no = getOutTradeNo()
    try:
        oresult = wxPay.order.create(trade_type='JSAPI', body=body, total_fee=totalfee, notify_url=notify_url,
                                     user_id=open_id, out_trade_no=out_trade_no, )

    except WeChatPayException, e:
        err = Error(msg=e.errmsg, type=4)
        # models.session.add(order)
        db.session.add(err)
        db.session.commit()
        return jsonify({'status': 'failed', 'orderId': order.id, 'msg': u"订单创建失败"})
    if oresult['return_code'] == 'SUCCESS':
        prepay_id = oresult['prepay_id']
        order.prepayid = prepay_id
        order.tradeno = out_trade_no
        order.status = 'waiting'
        order.detail = json.dumps(wxPay.jsapi.get_jsapi_params(prepay_id))
        # if order.ordertype != "continue":
        # car.count = car.count - 1
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
        if order.Car:
            order.Car.status = "normal"
        # order.Cartype.count = order.Cartype.count + 1
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


@api.route('/cancelotherorder/<id>')
@flask_login.login_required
def cancelOtherOrderApi(id):
    wxPay = wx.getPay()
    if wxPay.sandbox:
        sandKey = wxPay._fetch_sanbox_api_key()
        wxPay.sandbox_api_key = sandKey
    order = Otherorder.query.filter_by(id=id).first()
    if not order:
        return jsonify({"status": 'ok'})
    tradeNo = order.tradeno
    rr = wxPay.order.close(tradeNo)
    if rr['result_code'] == "SUCCESS":
        order.status = "canceled"
        order.detail = json.dumps(rr)
        order.Car.status = "normal"
        # order.Cartype.count = order.Cartype.count + 1
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": 'ok'})
    else:
        return jsonify({"status": 'failed'})


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
    if request.form.get("iscontinue") == "true" and request.form.get("orderid").isnumeric():
        sourceid = int(request.form.get("orderid"))
        sourceOrder = Order.query.filter_by(id=sourceid).first()
        sourceFromDate = sourceOrder.fromdate
        if not sourceFromDate:
            return jsonify({'status': 'error', 'code': 9, 'msg': "尚未发车，不能续租"})
        continueOrders = Order.query.filter_by(sourceid=sourceid).filter_by(status="ok").all()
        OrderSumData = getOrderSumData(sourceOrder, continueOrders)
        book_at = (sourceFromDate + dt.timedelta(days=OrderSumData["countSum"])).strftime('%Y-%m-%dT%H:%M:%S')
    # book_at = "2018-06-15T11:59:47"
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
    prefer = getFees(carTypeId, count, totalfee, openid, book_at)
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


# @api.route('/integral/<id>')
# @flask_login.login_required
# def getintegral(id):
#     customer = Customer.query.filter_by(id=id).first()
#     if customer and customer.openid == flask_login.current_user.openid:
#         return jsonify({"status": "ok","integral":customer.integral})
#     else:
#         return jsonify({"status":"failed"})

@api.route('/integralration/<type>')
@flask_login.login_required
def getintegralration(type):
    if type == 1:
        integral = Integral.query.filter_by(name=u"积分").first()
    elif type == 2:
        integral = Integral.query.filter_by(name=u"返点").first()
    else:
        integral = Integral.query.filter_by(name=u"兑现").first()
    if integral:
        return jsonify({"status": "ok", "ration": integral.ration})
    else:
        return jsonify({"status": "failed"})


@api.route('/integral', methods=['POST'])
@flask_login.login_required
def getintegral():
    fee = float(request.form.get("fee"))*100

    result = getIntegralCut(flask_login.current_user.openid, fee)
    return jsonify({"status": "ok", "result": result})


@api.route('/star/<id>')
@flask_login.login_required
def getStar(id):
    order = Order.query.filter_by(id=id).first()
    starCount = int(request.args.get("starCount"))
    if order and order.Customer.openid == flask_login.current_user.openid and order.ordertype == "normal":
        if not order.star and starCount <= 5 and starCount > 0:
            order.star = starCount
            commentIntegral = getComment()
            commentedIntegral = getCommented(starCount)
            order.Customer.integral = order.Customer.integral + commentIntegral
            db.session.add(order)
            db.session.commit()
            user = User.query.filter_by(id=order.Serverstop.userid).first()
            if user:
                customer = Customer.query.filter_by(openid=user.openid).first()
                if customer:
                    customer.integral = customer.integral + commentedIntegral
                    db.session.add(customer)
                    db.session.commit()
            return jsonify({"status": "ok", "integral": commentIntegral})
    return jsonify({"status": "error"})
