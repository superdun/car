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
       return render_template('car/error.html', data={'msg':u'抱歉，%s'%msg.decode('utf8')}, imgDomain="http://%s" % QINIU_DOMAIN)


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

            CarType = Cartype.query.filter(Cartype.status != "deleted").all()
            return returnError("未查询到相关订单")
            # return render_template('car/order.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))
        # try:
        #     wx_code = request.args.get("code")
        #     print wxAuth.get_user_info()
        #     return render_template('car/wechat/index.html')
        # except:
        #     return render_template('car/wechat/error.html')

@web.route('/cart/<id>')
def cart(id):
    if current_user.is_authenticated:
        if current_user.status == "normal":
            wxNonceStr = getRandomStr(15)
            wxTimeStamp = time.time()

            wxClient = wx.getClient()
            wxTicket = wxClient.jsapi.get_jsapi_ticket()
            url = current_app.config.get('WECHAT_URL') + url_for("web.selectCar")
            signature = wxClient.jsapi.get_jsapi_signature(wxNonceStr, wxTicket, wxTimeStamp, url)
            wxJSSDKConfig = {'url': url, 'signature': signature, 'nonceStr': wxNonceStr, 'timestamp': wxTimeStamp,
                             "appId": wx.getAppId()}

            wxPay = wx.getPay()
            CarType = Cartype.query.filter(Cartype.status != "deleted" and Cartype.id==id).first()
            if not CarType:
                return returnError("该车型暂时已满员，请选择其他车辆")
            return render_template('car/cart.html', carData=CarType, wxJSSDKConfig=wxJSSDKConfig,imgDomain="http://%s" % QINIU_DOMAIN)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))

@web.route('/MP_verify_KaJXT0CWMzGQXy1c.txt')
def wxVerufy():
    return current_app.config.get("WECHAT_VERYFI")

