# -*- coding:utf-8 -*-
from flask import current_app
import time
from wechatpy import oauth, client, pay
from ..models.dbORM import User
from ..helpers.other import getRandomStr


def getAppId():
    return current_app.config.get('WECHAT_APP_ID', '')


def getAppSecret():
    return current_app.config.get('WECHAT_APP_SECERET', '')


def getMchId():
    return current_app.config.get('WECHAT_MCH_ID', '')


def getPayApiKey():
    return current_app.config.get('WECAHT_PAY_API_KEY', '')


def getAuth():
    wxAppId = getAppId()
    wxAppsecret = getAppSecret()
    return oauth.WeChatOAuth(app_id=wxAppId, secret=wxAppsecret,
                             redirect_uri=current_app.config.get('WECHAT_URL') + current_app.config.get(
                                 'WECHAT_AUTH_REDIRECT_URL'), scope="snsapi_userinfo")


def getClient():
    wxAppId = getAppId()
    wxAppsecret = getAppSecret()
    from Session import session_interface
    return client.WeChatClient(appid=wxAppId, secret=wxAppsecret, session=session_interface())


def getPay():
    wxAppId = getAppId()
    wxPayApiKey = getPayApiKey()
    wxMchId = getMchId()
    mch_cert = current_app.config.get("WECHAT_CER_PATH")
    mch_key = current_app.config.get("WECHAT_CER_KEY_PATH")
    sandbox = current_app.config.get("WECAHT_PAY_SANDBOX")
    return pay.WeChatPay(appid=wxAppId, api_key=wxPayApiKey, mch_id=wxMchId, mch_cert=mch_cert, mch_key=mch_key,
                         timeout=None,
                         sandbox=sandbox)


def sendTemplate(openid, title, timeStr, orderType, customerInfo, carType, detail):
    template_id = current_app.config.get("WECHAT_MSG_MODEL_ID")
    data = {
        "first": {
            "value": title,
            "color": "#173177"
        },
        "keyword1": {
            "value": timeStr,
            "color": "#173177"
        },
        "keyword2": {
            "value": orderType,
            "color": "#173177"
        },
        "keyword3": {
            "value": customerInfo,
            "color": "#173177"
        },
        "keyword4": {
            "value": carType,
            "color": "#173177"
        },
        "remark": {
            "value": detail,
            "color": "#173177"
        }
    }
    wxClent = getClient()
    wxClent.message.send_template(openid, template_id, data)


def sendTemplateByOrder(order, description, type):
    admin = User.query.all()
    detail = u"电话：" + order.Customer.phone + u" 选择服务点：" + order.Serverstop.name + u" 定位地点：" + order.location + u" 预约时间：" + order.book_at + u"保险：" +order.Insure.name

    for i in admin:
        openid = i.openid
        if openid:
            sendTemplate(openid, description, order.created_at.strftime("%Y-%m-%d %H:%M:%S"), type,
                         order.Customer.name, order.Cartype.name + "*" + str(order.count), detail)
