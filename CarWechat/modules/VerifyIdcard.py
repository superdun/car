# -*- coding: utf-8 -*-
import requests
from flask import  current_app
def Verify(idcode,name):
    baseUrl = current_app.config.get("VERIFYIDCODEURL")
    appCode = current_app.config.get("VERIFYIDCODE_APPCODE")
    argsStr = "?cardNo="+idcode+"&realName="+name
    url = baseUrl+argsStr
    headers = {'Authorization':'APPCODE ' + appCode}
    r = requests.get(url,headers=headers)
    result =  r.json()
    if result["error_code"]==0:
        if result["result"]["isok"]:
            print "ok"
            return {"status":"ok","isok":True}
        else:
            return {"status": "ok", "isok": False}
    else:
        return {"status": "failed"}

