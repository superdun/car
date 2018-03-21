# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template,redirect,request,abort
from flask_login import login_required
from db.dbORM import *
from wechatpy import oauth,events
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
wechatView = Blueprint('wechat', __name__)
wxAppId = current_app.config.get('WECHAT_APP_ID', '')
wxAppsecret = current_app.config.get('WECHAT_APP_SECERET', '')
wxAuth = oauth.WeChatOAuth(app_id=wxAppId, secret=wxAppsecret,
                           redirect_uri="http://1o4958r317.51mypc.cn/wx/wx_authorize", scope="snsapi_userinfo")

@wechatView.route('/', methods=['GET', 'POST'])
def wechatIndex():
    token = current_app.config.get('WECHAT_TOKEN')
    encoding_aes_key = current_app.config.get('WECHAT_AESKEY')
    encrypt_mode = current_app.config.get('WECHAT_ENC_MODE')
    signature = request.args.get('signature',"")
    timestamp = request.args.get('timestamp',"")
    nonce = request.args.get('nonce',"")
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
@wechatView.route('/wx_getcode')
def wechatCode():
    print wxAuth.authorize_url
    return redirect(wxAuth.authorize_url)
@wechatView.route('/wx_authorize')
def wechatAuthorize():
    wx_code = request.args.get("code")
    wxAuth.fetch_access_token(wx_code)
    print wxAuth.get_user_info()
    return render_template('car/wechat/index.html')

    # try:
    #     wx_code = request.args.get("code")
    #     print wxAuth.get_user_info()
    #     return render_template('car/wechat/index.html')
    # except:
    #     return render_template('car/wechat/error.html')
