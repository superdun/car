# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template, redirect, request, abort, url_for, current_app, session
from flask_login import login_required, current_user
from ..helpers.thumb import upLoadFromUrl
from ..helpers.GetAllRealteOrders import getOrderSumData
from ..helpers.other import getRandomStr
from ..models.dbORM import *
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
)
from ..modules import Wechat as wx
import json
import time
import flask_login
from datetime import datetime
from ..helpers.getAdmin import getAdmin, getDownerAdmin
from app import login_manager, db

agentweb = Blueprint('agentweb', __name__)


@login_manager.user_loader
def user_loader(id):
    return Customer.query.filter_by(id=int(id)).first()


def getQiniuDomain():
    return current_app.config.get('QINIU_BUCKET_DOMAIN', '')


def wxAuth():
    return wx.getAuthForAgent()


def wxAuthOrder(orderid):
    return wx.getAuthForAgentOrder(orderid)


@agentweb.route('/', methods=['GET', 'POST'])
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
@agentweb.route('/wx_getcode')
def wechatCode():
    wxauth = wxAuth()

    return redirect(wxauth.authorize_url)


@agentweb.route('/wx_getcode_order/<id>')
def wechatCodeOrder(id):
    wxauth = wxAuthOrder(id)

    return redirect(wxauth.authorize_url)


@agentweb.route('/wx_authorize')
def wechatAuthorize():
    wx_code = request.args.get("code")
    wxauth = wxAuth()
    wxauth.fetch_access_token(wx_code)
    openId = wxauth.open_id
    customer = Customer.query.filter_by(openid=openId).first()
    if not customer:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})
    flask_login.login_user(customer)

    if not getAdmin(customer.openid):
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})
    return redirect(url_for("agentweb.order"))


@agentweb.route('/wx_authorize_order/<id>')
def wechatAuthorizeOrder(id):
    wx_code = request.args.get("code")
    wxauth = wxAuthOrder(id)
    wxauth.fetch_access_token(wx_code)
    openId = wxauth.open_id
    customer = Customer.query.filter_by(openid=openId).first()
    if not customer:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})
    flask_login.login_user(customer)

    if not getAdmin(customer.openid):
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})
    return redirect(url_for("agentweb.orderDetail", id=id))


@agentweb.route('/order')
@flask_login.login_required
def order():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        orderCount = current_app.config.get("ORDER_LIMIT")
        if not orderCount:
            orderCount = 30
        admins = getDownerAdmin(user)
        orderConfig = getOrderConfig()
        orders = Order.query.filter(
            Order.Serverstop.has(Serverstop.userid.in_([x.id for x in admins]))).filter(Order.status == "ok").filter(
            (Order.ordertype == None) | (Order.ordertype != "continue")).order_by(
            Order.id.desc()).limit(orderCount).all()

        return render_template("agent/order.html", data=orders, imgDomain="http://%s" % getQiniuDomain(),
                               orderConfig=orderConfig)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/order/<id>')
@flask_login.login_required
def orderDetail(id):
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    order = Order.query.filter_by(id=id).first()

    car = order.Cartype.cars
    if current_user.is_authenticated and user and order:
        admins = getDownerAdmin(user)
        continueOrders = Order.query.filter_by(sourceid=id).filter_by(status="ok").all()
        OrderSumData = getOrderSumData(order, continueOrders)
        orderConfig = getOrderConfig()
        if order.Serverstop.userid not in ([x.id for x in admins]):
            return render_template("agent/error.html", data={'msg': u'抱歉，未找到订单'})
        if order.fromdate:
            imgs = [order.proofimg,order.carbeforeimg,order.carendimg]
            if order.todate:
                return render_template("agent/orderDetail.html", data=order, imgDomain="http://%s" % getQiniuDomain(),
                                       orderConfig=orderConfig, OrderSumData=OrderSumData,
                                       continueOrders=continueOrders,imgs=imgs)
            else:
                return render_template("agent/carback.html", data=order, imgDomain="http://%s" % getQiniuDomain(),
                                       orderConfig=orderConfig, OrderSumData=OrderSumData,
                                       continueOrders=continueOrders,imgs=imgs)

        else:
            return render_template("agent/depart.html", data=order, imgDomain="http://%s" % getQiniuDomain(),
                                   orderConfig=orderConfig, car=car, OrderSumData=OrderSumData,
                                   continueOrders=continueOrders)


@agentweb.route('/accident')
@flask_login.login_required
def accident():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        orderCount = current_app.config.get("ORDER_LIMIT")
        data = Accident.query.filter_by(userid=user.id).order_by(
            Accident.id.desc()).limit(orderCount).all()
        return render_template("agent/accident.html", data=data, imgDomain="http://%s" % getQiniuDomain())
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/accident/new')
@flask_login.login_required
def accidentNew():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        orderid = request.args.get("orderid")
        carid = request.args.get("carid")
        car = Car.query.filter_by(id=carid).first()
        cartypes = Cartype.query.all()
        return render_template("agent/accidentDetail.html", car=car, orderid=orderid, cartypes=cartypes, data=None)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/accident/<id>')
@flask_login.login_required
def accidentDetail(id):
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        cartypes = Cartype.query.all()
        data = Accident.query.filter_by(id=id).first()
        orderid = data.orderid
        car = data.Car
        data.created_at = data.created_at.strftime('%Y-%m-%dT%H:%M:%S')
        imgs = [data.img1, data.img2, data.img3, data.img4, data.img5, data.img6]
        imgList = {}

        imgList = json.dumps(imgList)
        return render_template("agent/accidentDetail.html", car=car, orderid=orderid, cartypes=cartypes, data=data,
                               imgs=imgs)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/move')
@flask_login.login_required
def move():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        orderCount = current_app.config.get("ORDER_LIMIT")
        data = Move.query.filter_by(userid=user.id).order_by(
            Move.id.desc()).limit(orderCount).all()
        return render_template("agent/move.html", imgDomain="http://%s" % getQiniuDomain(), data=data)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/move/new')
@flask_login.login_required
def moveNew():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        cartypes = Cartype.query.all()
        serverstops = Serverstop.query.all()
        return render_template("agent/moveDetail.html", cartypes=cartypes, serverstops=serverstops, data=None)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/move/<id>')
@flask_login.login_required
def moveDetail(id):
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        cartypes = Cartype.query.all()
        serverstops = Serverstop.query.all()
        data = Move.query.filter_by(id=id).first()
        data.created_at = data.created_at.strftime('%Y-%m-%dT%H:%M:%S')
        fromS = Serverstop.query.filter_by(id=data.fromid).first()
        toS = Serverstop.query.filter_by(id=data.toid).first()

        return render_template("agent/moveDetail.html", cartypes=cartypes, serverstops=serverstops, data=data,
                               fromS=fromS, toS=toS)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/apply')
@flask_login.login_required
def apply():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        orderCount = current_app.config.get("ORDER_LIMIT")
        data = Apply.query.filter_by(userid=user.id).order_by(
            Apply.id.desc()).limit(orderCount).all()
        return render_template("agent/apply.html", imgDomain="http://%s" % getQiniuDomain(), data=data)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})


@agentweb.route('/apply/new')
@flask_login.login_required
def applyNew():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:
        cartypes = Cartype.query.all()
        return render_template("agent/applyDetail.html", cartypes=cartypes)
    else:
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员'})
