# -*- coding:utf-8 -*-
from flask import current_app,url_for
import time
from wechatpy import oauth, client, pay
from ..models.dbORM import User
from ..helpers.other import getRandomStr
from ..helpers.getAdmin import getAdmin, getUperAdmin


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


def getAuthForAgent():
    wxAppId = getAppId()
    wxAppsecret = getAppSecret()
    return oauth.WeChatOAuth(app_id=wxAppId, secret=wxAppsecret,
                             redirect_uri=current_app.config.get('WECHAT_URL') + current_app.config.get(
                                 'WECHAT_AUTH_REDIRECT_URL_FOR_AGENT'), scope="snsapi_userinfo")

def getAuthForAgentOrder(orderid):
    wxAppId = getAppId()
    wxAppsecret = getAppSecret()
    return oauth.WeChatOAuth(app_id=wxAppId, secret=wxAppsecret,
                             redirect_uri=current_app.config.get('WECHAT_URL') + current_app.config.get(
                                 'WECHAT_AUTH_REDIRECT_URL_FOR_AGENT_ORDER')+str(orderid), scope="snsapi_userinfo")


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


def sendTemplate(openid, title, timeStr, orderType, customerInfo, carType, detail,url=""):
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
    wxClent.message.send_template(openid, template_id, data,url=url )
def sendIntegralTemplate(openid, title, typeStr, integral, total, detail,url=""):
    template_id = current_app.config.get("WECHAT_MSG_MODEL_ID_INTEGRAL")
    data = {
        "first": {
            "value": title,
            "color": "#173177"
        },
        "type": {
            "value": typeStr,
            "color": "#173177"
        },
        "integral": {
            "value": integral,
            "color": "#173177"
        },
        "all": {
            "value": total,
            "color": "#173177"
        },
        "remark": {
            "value": detail,
            "color": "#173177"
        }
    }
    wxClent = getClient()
    wxClent.message.send_template(openid, template_id, data,url=url )
def sendOvertimeTemplate(openid, title, name, expDate, detail,url=""):
    template_id = current_app.config.get("WECHAT_MSG_MODEL_ID_OVERTIME")
    data = {
        "first": {
            "value": title,
            "color": "#173177"
        },
        "name": {
            "value": name,
            "color": "#173177"
        },
        "expDate": {
            "value": expDate,
            "color": "#173177"
        },
        "remark": {
            "value": detail,
            "color": "#173177"
        }
    }
    wxClent = getClient()
    wxClent.message.send_template(openid, template_id, data,url=url )

def sendTemplateByOrder(order, description, type,url=""):
    user = order.Serverstop.User
    admin =getUperAdmin(user)
    # admin = User.query.all()
    if order.Insure:
        insureName = order.Insure.name
    else:
        insureName = u"无"
    detail = u"电话：" + order.Customer.phone + u" 选择服务点：" + order.Serverstop.name + u" 定位地点：" + order.location + u" 预约时间：" + order.book_at + u"保险：" + insureName
    if order.ordertype=="continue":
        type = type+u" 续租"
    for i in admin:
        openid = i.openid
        if openid:
            try:
                sendTemplate(openid, description, order.created_at.strftime("%Y-%m-%d %H:%M:%S"), type,
                         order.Customer.name, order.Cartype.name + "*" + str(order.count), detail,url)
            except:
                pass
def sendIntegralTemplateByCustomer(customer, count,typeStr):

    openid = customer.openid

    if openid:
        title = u"尊敬的%s,通力币最近交易信息如下：" % customer.name
        detail=u"如有疑问,请随时咨询代理"
        url = current_app.config.get('WECHAT_HOST') + url_for("web.profile")
        try:
            sendIntegralTemplate(openid,title,typeStr,count,customer.integral,detail,url)
        except:
            pass