from flask import current_app
import time
from wechatpy import oauth,client,pay

from helpers.other import getRandomStr
def getAppId():
    return current_app.config.get('WECHAT_APP_ID', '')

def getAppSecret():
    return  current_app.config.get('WECHAT_APP_SECERET', '')

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
    return client.WeChatClient(appid=wxAppId, secret=wxAppsecret, session=session_interface)

def getPay():
    wxAppId = getAppId()
    wxPayApiKey = getPayApiKey()
    wxMchId = getMchId()
    mch_cert  = current_app.config.get("WECHAT_CER_PATH")
    mch_key = current_app.config.get("WECHAT_CER_KEY_PATH")
    return pay.WeChatPay(appid=wxAppId, api_key=wxPayApiKey, mch_id= wxMchId,  mch_cert=mch_cert, mch_key=mch_key, timeout=None,
                           sandbox=False)
