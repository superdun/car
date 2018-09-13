# -*- coding:utf-8 -*-
from flask import current_app,url_for
import config
from wechatpy import oauth, client, pay
from dbORM import User
from getAdmin import getAdmin, getUperAdmin


def getAppId():
    return config.WECHAT_APP_ID


def getAppSecret():
    return config.WECHAT_APP_SECERET



def getClient():
    wxAppId = getAppId()
    wxAppsecret = getAppSecret()
    from Session import session_interface
    return client.WeChatClient(appid=wxAppId, secret=wxAppsecret, session=session_interface())


def sendOvertimeTemplate(openid, title, name, expDate, detail,url=""):
    template_id = config.WECHAT_MSG_MODEL_ID_OVERTIME
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

def sendTemplateByOrder(order,expDate):
    user = order.Serverstop.User
    admin =getUperAdmin(user)
    # admin = User.query.all()
    title = u"您的车辆即将到期，请及时还车"
    name = order.Car.name
    detail = u""
    for i in admin:
        openid = i.openid
        if openid:
            sendOvertimeTemplate(openid, title, name, expDate, detail)
            # try:
            #     sendOvertimeTemplate(openid,title,name,expDate,detail)
            # except:
            #     pass
