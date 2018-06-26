# -*- coding: utf-8 -*-
from CarAdmin.app.modules.CarSDK import CarOlineApi
from config import *

from werkzeug.contrib.cache import RedisCache
from sqlalchemy import create_engine
import dbORM
import time
def cache():
    host = REDIS_HOST
    port = REDIS_PORT
    return RedisCache(host, port)

def getcarApi():
    account = CAR_ACCOUNT
    password = CAR_PASSWORD
    return CarOlineApi(account=account, password=password)

def carMonitor():
    carapi = getcarApi()
    carapi.getToken()
    Cache = cache()
    session = dbORM.DBSession()
    carObjs = session.query(dbORM.Gps).all()
    for carObj in carObjs:

        i = carapi.tracking(carObj.code)["data"]
        if len(i)==0:
            print carapi.tracking(carObj.code)
            Cache.set(carObj.code, {}, CAR_CACHE_TIMEOUT)
            continue
        else:
            i =i[0]
        if carObj and carObj.cars:

            ar = carapi.address(i["lng"],i["lat"])
            outprovice = 0

            try:
                address = ar["address"]
                if address and address[0]!=u"辽":
                    outprovice = 1

            except:
                address = ""
            try:

                carId = carObj.cars[0].id
                carName = carObj.cars[0].name
                carImg = carObj.cars[0].img
            except:
                carId = ""
                carName = ""
                carImg = ""
        else:
            carId = ""
            carName = ""
            carImg = ""
        i['car'] = {'id': carId, 'name': carName, 'img': carImg}
        i["address"] = address
        i["outprovice"] = outprovice
        Cache.set(carObj.code,i,CAR_CACHE_TIMEOUT)
        time.sleep(0.1)
    print " Done!"
if __name__ == '__main__':
    carMonitor()

