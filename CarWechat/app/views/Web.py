# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template, redirect, request, abort, url_for, current_app, session
from flask_login import login_required, current_user
from ..helpers.thumb import upLoadFromUrl
from ..helpers.other import getRandomStr
from ..helpers.GetAllRealteOrders import getOrderSumData
from ..models.dbORM import *
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
)
from ..modules import Wechat as wx

import time
import flask_login
from datetime import datetime
from app import login_manager, db

web = Blueprint('web', __name__)


@login_manager.user_loader
def user_loader(id):
    return Customer.query.filter_by(id=int(id)).first()


def getQiniuDomain():
    return current_app.config.get('QINIU_BUCKET_DOMAIN', '')


def wxAuth():
    return wx.getAuth()


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
                           imgDomain="http://%s" % getQiniuDomain())


def getJSSDK(url):
    wxNonceStr = getRandomStr(15)
    wxTimeStamp = int(time.time())

    wxClient = wx.getClient()
    wxTicket = wxClient.jsapi.get_jsapi_ticket()

    signature = wxClient.jsapi.get_jsapi_signature(wxNonceStr, wxTicket, wxTimeStamp, url)

    return {'url': url, 'signature': signature, 'nonceStr': wxNonceStr, 'timestamp': wxTimeStamp,
            "appId": wx.getAppId()}


def getOrderConfig():
    return current_app.config.get("ORDER_STATUS")


# @web.route('/index')
# def wechatIndex():
#     if
#     return redirect(wxAuth.authorize_url)
@web.route('/wx_getcode')
def wechatCode():
    wxauth = wxAuth()
    print wxauth.authorize_url
    return redirect(wxauth.authorize_url)


@web.route('/wx_authorize')
def wechatAuthorize():
    wx_code = request.args.get("code")
    wxauth = wxAuth()
    wxauth.fetch_access_token(wx_code)
    openId = wxauth.open_id
    userInfo = wxauth.get_user_info(openId)
    img = upLoadFromUrl(userInfo["headimgurl"], openId)
    customer = Customer.query.filter_by(openid=openId).first()
    if not customer:
        customer = Customer(openid=openId, status="pending", img=img, created_at=datetime.now())

        db.session.add(customer)
        db.session.commit()
    flask_login.login_user(customer)

    if customer.status == "pending":
        return redirect(url_for("web.wechatSign"))
    return redirect(url_for("web.selectCar"))


@web.route('/sign')
def wechatSign():
    return render_template('car/sign.html', imgDomain="http://%s" % getQiniuDomain())


@web.route('/selectcar')
def selectCar():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            CarType = Cartype.query.filter(Cartype.status != "deleted").all()
            CarCat = Carcat.query.all()
            return render_template('car/selectCar.html', data=CarType, cat=CarCat,
                                   imgDomain="http://%s" % getQiniuDomain(),
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
            orders = Order.query.filter_by(customeropenid=openId).filter((Order.ordertype==None)|(Order.ordertype!="continue")).order_by(Order.id.desc()).all()
            return render_template("car/order.html", data=orders, imgDomain="http://%s" % getQiniuDomain(),
                                   orderConfig=orderConfig)
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
            if order.ordertype=="continue":
                order = Order.query.filter_by(id = order.sourceid).first()
                id = order.id
            continueOrders = Order.query.filter_by(sourceid=id).filter_by(status="ok").all()
            if not order:
                return returnError("未找到相关订单")
            OrderSumData=getOrderSumData(order,continueOrders)
            orderConfig = getOrderConfig()
            import json

            if order.status == "waiting" :
                wxJSSDKPayConfig = json.loads(order.detail)
                return render_template("car/repay.html", data=order, imgDomain="http://%s" % getQiniuDomain(),
                                       wxJSSDKPayConfig=wxJSSDKPayConfig, wxJSSDKConfig=wxJSSDKConfig,
                                       orderConfig=orderConfig)
            else:
                return render_template('car/orderDetail.html', data=order, imgDomain="http://%s" % getQiniuDomain(),
                                       orderConfig=orderConfig,continueOrders=continueOrders,OrderSumData=OrderSumData)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/profile')
def profile():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            openId = current_user.openid
            customer = Customer.query.filter_by(openid=openId).first()
            if customer:
                return render_template("car/profile.html", data=customer, imgDomain="http://%s" % getQiniuDomain())
            else:
                return redirect(url_for("web.wechatSign"))
                # return render_template('car/order.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/map')
def map():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            url = current_app.config.get('WECHAT_HOST') + url_for("web.map")
            wxJSSDKConfig = getJSSDK(url)

            return render_template('car/map.html', wxJSSDKConfig=wxJSSDKConfig,
                                   imgDomain="http://%s" % getQiniuDomain())
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/cart/<id>')
def cart(id):
    if current_user.is_authenticated:
        if current_user.status == "normal":

            isContinue = request.args.get("isContinue")
            # url = current_app.config.get('WECHAT_HOST') + url_for("web.cart", id=id)
            url=request.url
            wxJSSDKConfig = getJSSDK(url)

            CarType = Cartype.query.filter(Cartype.status != "deleted" and Cartype.id == id).first()
            integralSwitch = Integral.query.filter_by(name=u"开关").first()
            integralIsOpen = False
            if  integralSwitch and int(integralSwitch.ration) == 1:
                integralIsOpen = True
            if isContinue == "true":
                orderid = int(request.args.get("orderid"))
                sourceOrder = Order.query.filter_by(id=orderid).first()
                if not sourceOrder.fromdate:
                    return returnError("您的订单尚未配送发车，无法续租")
                return render_template('car/continuecart.html', carData=CarType, wxJSSDKConfig=wxJSSDKConfig,
                                       imgDomain="http://%s" % getQiniuDomain(), sourceOrder=sourceOrder,integralIsOpen=integralIsOpen)
                # try:
                #
                #
                #     orderid = int(request.args.get("orderid"))
                #     sourceOrder = Order.query.filter_by(id=orderid).first()
                #     return render_template('car/continuecart.html', carData=CarType, wxJSSDKConfig=wxJSSDKConfig,
                #                            imgDomain="http://%s" % getQiniuDomain(), sourceOrder=sourceOrder)
                #
                # except:
                #     return returnError("账号存在风险，请联系管理员")
            else:
                openid = current_user.openid
                orders = Order.query.filter_by(customeropenid=openid).filter(Order.ordertype!="continue").filter(
                    (Order.orderstatus == "start") | (Order.orderstatus == "depart")).first()
                if orders:
                    # if orders.carid != id:
                    return returnError("您还有未完成订单，如有需求请<a href='%s'>续租</a>，或联系管理员"%url_for("web.orderDetail",id=orders.id))
            ServerStop = Serverstop.query.all()
            InSure = Insure.query.all()
            if not CarType:
                return returnError("该车型暂时已满员，请选择其他车辆")
            return render_template('car/cart.html', carData=CarType, wxJSSDKConfig=wxJSSDKConfig,
                                   imgDomain="http://%s" % getQiniuDomain(), serverstop=ServerStop, insure=InSure,integralIsOpen=integralIsOpen)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/contract')
def wxContract():
    return render_template("car/inform.html")


@web.route('/MP_verify_KaJXT0CWMzGQXy1c.txt')
def wxVerufy():
    return current_app.config.get("WECHAT_VERYFI")
