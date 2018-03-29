# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template, redirect, request, abort, url_for, current_app, session
from flask_login import login_required, current_user
from helpers.thumb import upLoadFromUrl
from helpers.other import getRandomStr
from db.dbORM import *
from wechatpy import oauth, events
from wechatpy import parse_message, create_reply, client
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)

import time
import flask_login

web = Blueprint('web', __name__)

QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')

wxAppId = current_app.config.get('WECHAT_APP_ID', '')
wxAppsecret = current_app.config.get('WECHAT_APP_SECERET', '')
wxAuth = oauth.WeChatOAuth(app_id=wxAppId, secret=wxAppsecret,
                           redirect_uri=current_app.config.get('WECHAT_URL') + current_app.config.get(
                               'WECHAT_AUTH_REDIRECT_URL'), scope="snsapi_userinfo")

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
    wxNonceStr = getRandomStr(15)
    wxTimeStamp = time.time()
    from modules.Session import session_interface
    wxClient = client.WeChatClient(appid=wxAppId, secret=wxAppsecret, session=session_interface)
    wxTicket = wxClient.jsapi.get_jsapi_ticket()
    url = current_app.config.get('WECHAT_URL') + url_for("web.selectCar")
    signature = wxClient.jsapi.get_jsapi_signature(wxNonceStr, wxTicket, wxTimeStamp, url)
    wxJSSDKConfig = {'url': url, 'signature': signature, 'nonceStr': wxNonceStr, 'timestamp': wxTimeStamp,
                     "appId": wxAppId}
    if current_user.is_authenticated:
        if current_user.status == "normal":
            CarType = Cartype.query.filter(Cartype.status != "deleted").all()
            return render_template('car/selectCar.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN,
                                   wxJSSDKConfig=wxJSSDKConfig)
        else:
            return redirect(url_for("web.wechatSign"))

    else:
        return redirect(url_for('web.wechatSign'))


@web.route('/order')
def order():
    if current_user.is_authenticated:
        if current_user.status == "normal":
            CarType = Cartype.query.filter(Cartype.status != "deleted").all()
            return render_template('car/order.html', data=CarType, imgDomain="http://%s" % QINIU_DOMAIN)
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


@web.route('/MP_verify_KaJXT0CWMzGQXy1c.txt')
def wxVerufy():
    return current_app.config.get("WECHAT_VERYFI")
