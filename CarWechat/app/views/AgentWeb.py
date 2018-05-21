# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template, redirect, request, abort, url_for, current_app, session
from flask_login import login_required, current_user
from ..helpers.thumb import upLoadFromUrl
from ..helpers.other import getRandomStr
from ..models.dbORM import *
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
)
from ..modules import  Wechat as wx

import time
import flask_login
from datetime import datetime
from app import login_manager,db

agentweb = Blueprint('agentweb', __name__)




@login_manager.user_loader
def user_loader(id):
    return Customer.query.filter_by(id=int(id)).first()

def getQiniuDomain():
    return current_app.config.get('QINIU_BUCKET_DOMAIN', '')

def wxAuth():

    return wx.getAuthForAgent()







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
    print wxauth.authorize_url
    return redirect(wxauth.authorize_url)
def getAdmin(openid):

    user = User.query.filter_by(openid=openid).first()
    return user
def getConstruct():
    pass
def getUperAdmin(user):
    result = []
    admins = Userrole.query.filter_by(stage=1).first().users
    for i in admins:
        result.append(i)
    if user.Userrole.stage == 2:
        result.append(user)
    if user.Userrole.stage == 3:
        result.append(user)
        up = User.query.filter_by(id=user.upid).first()
        if up:
            result.append(up)
    return result
def getDownerAdmin(user):
    result = []

    if user.Userrole.stage == 1:
        admins =  User.query.all()
        for i in admins:
            result.append(i)
    if user.Userrole.stage == 2:
        result.append(user)
        downs = user.down
        for i in downs:
            result.append(i)
    if user.Userrole.stage == 3:
        result.append(user)
    return result
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
        return render_template("agent/error.html", data={'msg': u'抱歉，您不是管理员' })
    return redirect(url_for("agentweb.order"))



@agentweb.route('/order')
@flask_login.login_required
def order():
    try:
        user = getAdmin(current_user.openid)
    except:
        return render_template(url_for("agentweb.error"), data={'msg': u'请登陆'})
    if current_user.is_authenticated and user:

        admins = getDownerAdmin(user)
        orderConfig = getOrderConfig()
        orders = db.session.query(Order).filter(Order.Serverstop.has(Serverstop.userid.in_([x.id for x in admins])  )).filter(Order.status == "ok").order_by(Order.id.desc()).all()
        return render_template("agent/order.html", data=orders,imgDomain="http://%s" % getQiniuDomain(),orderConfig=orderConfig)
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
        orderConfig = getOrderConfig()
        if order.Serverstop.userid not in ([x.id for x in admins]):
            return render_template("agent/error.html", data={'msg': u'抱歉，未找到订单'})
        if order.fromdate:
            if order.todate:
                return render_template("agent/orderDetail.html",data=order, imgDomain="http://%s" % getQiniuDomain(),orderConfig=orderConfig)
            else:
                return render_template("agent/carback.html",data=order, imgDomain="http://%s" % getQiniuDomain(),orderConfig=orderConfig)

        else:
            return render_template("agent/depart.html",data=order, imgDomain="http://%s" % getQiniuDomain(),orderConfig=orderConfig,car=car)