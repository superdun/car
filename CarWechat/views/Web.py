# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template, redirect, request, abort, url_for, current_app, session
from flask_login import login_required, current_user
from helpers.thumb import upLoadFromUrl
from helpers.other import getRandomStr
from db.dbORM import *
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
)
import modules.Wechat as wx

import time
import flask_login

web = Blueprint('web', __name__)

QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')

wxAuth = wx.getAuth()

login_manager = flask_login.LoginManager()

login_manager.init_app(current_app)


@login_manager.user_loader
def user_loader(id):
    return Customer.query.filter_by(id=int(id)).first()


@web.route('/', methods=['GET', 'POST'])
def wechatIndex():
    token = current_app.config.get('WECHAT_TOKEN')
    encoding_aes_key = current_app.config.get('WECHAT_AESKEY')
    encrypt_mode = current_app.config.get('WECHAT_ENC_MODE')
    signature = request.args.get('signature', "")
    timestamp = request.args.get('timestamp', "")
    nonce = request.args.get('nonce', "")
    encrypt_type = request.args.get('encrypt_type', 'raw')
    try:
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    if request.method == 'GET':
        echo_str = request.args.get('echostr', '')
        return echo_str
    else:
        if encrypt_type == 'raw':
            # plaintext mode
            msg = parse_message(request.data)
            print msg.type
            if msg.type == 'text':
                reply = create_reply(msg.content, msg)
            elif msg.type == 'event':
                # evt = events.SubscribeEvent(msg)
                print msg.source
                reply = create_reply(msg.source, msg)
            else:
                reply = create_reply('Sorry, can not handle this for now', msg)
            return reply.render()
            # echostr = request.args.get('echostr')
            # return echostr
            # return redirect(wxAuth.authorize_url)


def returnError(msg):
    return render_template('car/error.html', data={'msg': u'抱歉，%s' % msg.decode('utf8')},
                           imgDomain="http://%s" % QINIU_DOMAIN)


def getJSSDK(url):
    wxNonceStr = getRandomStr(15)
    wxTimeStamp = int(time.time())

    wxClient = wx.getClient()
    wxTicket = wxClient.jsapi.get_jsapi_ticket()

    signature = wxClient.jsapi.get_jsapi_signature(wxNonceStr, wxTicket, wxTimeStamp, url)

    return {'url': url, 'signature': signature, 'nonceStr': wxNonceStr, 'timestamp': wxTimeStamp,
            "appId": wx.getAppId()}
@current_app.template_filter('cutstring')
def reverse_filter(s):
    return u'%s******%s'%(s[0:4],s[-4:])
def getOrderConfig():
    return current_app.config.get("ORDER_STATUS")
# @web.route('/index')
# def wechatIndex():
#     if
#     return redirect(wxAuth.authorize_url)
@web.route('/wx_getcode')
def wechatCode():
    print wxAuth.authorize_url
    return redirect(wxAuth.authorize_url)


@web.route('/wx_authorize')
def wechatAuthorize():
    wx_code = request.args.get("code")
    wxAuth.fetch_access_token(wx_code)
    openId = wxAuth.open_id
    userInfo = wxAuth.get_user_info(openId)
    img = upLoadFromUrl(userInfo["headimgurl"], openId)
    customer = Customer.query.filter_by(openid=openId).first()
    if not customer:
        customer = Customer(openid=openId, status="pending", img=img)

        db.session.add(customer)
        db.session.commit()
    flask_login.login_user(customer)

    if customer.status == "pending":
        return redirect(url_for("web.wechatSign"))
    return redirect(url_for("web.selectCar"))


@web.route('/sign')
def wechatSign():
    return render_template('car/sign.html', imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/selectcar')
def selectCar():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            CarType = Cartype.query.filter(Cartype.status != "deleted").all()
            return render_template('car/selectCar.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN,
                                   )
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/order')
def order():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            orderConfig = getOrderConfig()
            openId = current_user.openid
            orders = Order.query.filter_by(userid=openId).all()
            return render_template("car/order.html", data=orders, imgDomain="http://%s" % QINIU_DOMAIN,orderConfig=orderConfig)
            # return render_template('car/order.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/order/<id>')
def orderDetail(id):
    if current_user.is_authenticated:
        if current_user.status == "normal":
            url = current_app.config.get('WECHAT_HOST') + url_for("web.orderDetail", id=id)
            wxJSSDKConfig = getJSSDK(url)
            openId = current_user.openid
            order = Order.query.filter_by(id=id).first()
            if not order:
                return returnError("未找到相关订单")
            orderConfig = getOrderConfig()
            import json
            if order.status=="waiting":
                wxJSSDKPayConfig = json.loads(order.detail)
                return render_template("car/repay.html", data=order, imgDomain="http://%s" % QINIU_DOMAIN,
                                   wxJSSDKPayConfig=wxJSSDKPayConfig, wxJSSDKConfig=wxJSSDKConfig,orderConfig=orderConfig)
            else :
                return render_template('car/orderDetail.html', data=order, imgDomain="http://%s" % QINIU_DOMAIN,orderConfig=orderConfig)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/cart/<id>')
def cart(id):
    if current_user.is_authenticated:
        if current_user.status == "normal":
            url = current_app.config.get('WECHAT_HOST') + url_for("web.cart", id=id)
            wxJSSDKConfig = getJSSDK(url)

            CarType = Cartype.query.filter(Cartype.status != "deleted" and Cartype.id == id).first()
            if not CarType:
                return returnError("该车型暂时已满员，请选择其他车辆")
            return render_template('car/cart.html', carData=CarType, wxJSSDKConfig=wxJSSDKConfig,
                                   imgDomain="http://%s" % QINIU_DOMAIN)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/MP_verify_KaJXT0CWMzGQXy1c.txt')
def wxVerufy():
    return current_app.config.get("WECHAT_VERYFI")
