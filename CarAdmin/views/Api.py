# -*- coding:utf-8 -*-
from  flask import Blueprint, jsonify, request, current_app, url_for

from db.dbORM import *
from modules.CarSDK import CarOlineApi
import modules.Wechat as wx
import flask_login

from datetime import datetime
from wechatpy.utils import timezone
import time
import json
import random

api = Blueprint('api', __name__)
account = current_app.config.get('CAR_ACCOUNT', '')
password = current_app.config.get('CAR_PASSWORD', '')
carApi = CarOlineApi(account=account, password=password)


def getOutTradeNo():
    now = datetime.fromtimestamp(time.time(), tz=timezone('Asia/Shanghai'))
    return '{0}{1}{2}'.format(
        current_app.config.get("WECHAT_MCH_ID"),
        now.strftime('%Y%m%d%H%M%S'),
        random.randint(1000, 10000)
    )


def getRefundResult(s, key):
    import base64
    from Crypto.Cipher import AES
    import hashlib
    hl = hashlib.md5()
    hl.update(key)
    newkey = hl.hexdigest()
    mode = AES.MODE_ECB
    iv = 16 * '\x00'
    decryptor = AES.new(newkey, mode, IV=iv)
    a = base64.b64encode(s)
    return decryptor.decrypt(a)


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
        return jsonify({'status': 'ok', 'msg': data['msg'], 'data': data['data']})
    else:
        return jsonify({'status': 'error', 'msg': data['msg'], 'data': []})


@api.route('/api/carmonitor/<id>')
def oneCarMonitorApi(id):
    carApi.getToken()
    car = Car.query.get(id)
    data = carApi.tracking(car.imei)
    return jsonify(data)


@api.route('/api/getrefundresult', methods=["POST"])
def getRefundResult():
    wxPay = wx.getPay()
    if wxPay.sandbox:
        sandKey = wxPay._fetch_sanbox_api_key()
        wxPay.sandbox_api_key = sandKey
    try:
        r = wxPay.parse_payment_result(request.data)


    except InvalidSignatureException:
        return
    if r["return_code"] == "SUCCESS":
        rawr = r["req_info"]
        if wxPay.sandbox:
            sandKey = wxPay._fetch_sanbox_api_key()
            r = getRefundResult(rawr, sandKey)
        else:
            r = getRefundResult(rawr, getPayApiKey())

        order = Order.query.filter_by(tradeno=r["out_trade_no"]).first()
        if not order:
            e = Error(msg=json.dumps(r), type=1)
            db.session.add(e)
            db.session.commit()
        else:
            if r["refund_status"] == "SUCCESS":
                order.status = "refunded"
                order.r_pay_at = r["success_time"]
                order.r_totalfee = r["settlement_refund_fee"]
                order.r_Detail = json.dumps(r)
    return "ok"


@api.route('/api/refreshrefundresult')
def refreshRefundResult():
    wxPay = wx.getPay()
    if wxPay.sandbox:
        sandKey = wxPay._fetch_sanbox_api_key()
        wxPay.sandbox_api_key = sandKey
    orders = Order.query.filter_by(status="refundconfirmed").all()
    for i in orders:
        refund_id = i.r_wxtradeno
        out_refund_no = i.r_tradeno
        transaction_id = i.wxtradeno
        out_trade_no = i.tradeno
        r = wxPay.refund.query(refund_id=refund_id, out_refund_no=out_refund_no, transaction_id=transaction_id,
                               out_trade_no=out_trade_no)
        for k in range(int(r['refund_count'])):
            if r["refund_status_%d"%k]=="SUCCESS":
                i.status="refunded"
                i.r_pay_at=r["refund_success_time_%d"%k]
                i.r_totalfee = r["refund_fee_%d" % k]
                i.r_detail = json.dumps(r)
                db.session.add(i)

                db.session.commit()
    return jsonify({"status":"ok"})

@api.route('/api/refund/<id>')
def refundApplyApi(id):
    if flask_login.current_user.is_authenticated:
        if request.args.get("isconfirm")=="True":
            isconfirm = True
        else:
            isconfirm = False
        order = Order.query.filter_by(id=id).first()
        if not isconfirm:
            order.status = 'refundfailed'
            db.session.add(order)
            db.session.commit()
        else:
            wxPay = wx.getPay()
            if wxPay.sandbox:
                sandKey = wxPay._fetch_sanbox_api_key()
                wxPay.sandbox_api_key = sandKey

            total_fee = int(order.totalfee)
            refund_fee = int(total_fee)
            refund_no = getOutTradeNo()
            transaction_id = order.wxtradeno
            # total_fee = 1
            # refund_fee = 1
            # refund_no = getOutTradeNo()
            # transaction_id = "4200000098201804052954108790"

            notify_url = current_app.config.get('WECHAT_HOST') + url_for('api.getRefundResult')

            rr = wxPay.refund.apply(total_fee=total_fee, refund_fee=refund_fee, out_refund_no=refund_no,
                                         transaction_id=transaction_id)
            # try:
            #     rr = wxPay.refund.apply(total_fee=total_fee, refund_fee=refund_fee, out_refund_no=refund_no,
            #                             transaction_id=transaction_id)
            # except:
            #
            #     return jsonify({"status": 'failed'})
            if rr['result_code'] == "SUCCESS":
                order.status = "refundconfirmed"
                order.r_tradeno = refund_no
                order.r_totalfee = rr["refund_fee"]
                order.r_wxtradeno = rr['refund_id']
                db.session.add(order)

                db.session.commit()
                return jsonify({"status": 'ok'})
            else:

                return jsonify({"status": 'failed'})

        return jsonify({"status": 'ok'})
