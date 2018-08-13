# -*- coding:utf-8 -*-
from ..models.dbORM import *
import datetime
from datetime import datetime as dtt
from math import floor

def getIntegralCut(openid,fee):
    fee = int(fee)
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    integral = Integral.query.filter_by(name=u"兑现").first()
    customer = Customer.query.filter_by(openid=openid).first()
    customerIntegral = customer.integral
    if customerIntegral==0 or not integral or not customer or not integralSwitch or not int(integralSwitch.ration)==1:
        return {"cut":0,"used":0}
    else:
        ration = integral.ration
        cutSum = (floor(customerIntegral*ration*100))/100
        if cutSum<fee:
            return {"cut": cutSum, "used": customerIntegral}
        else:
            return {"cut": fee, "used": int(floor(fee/ration))}

def getIntegralImprove(fee):
    fee = int(fee)
    integral = Integral.query.filter_by(name=u"积分").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration*fee)
    return 0
def getRecomend():

    integral = Integral.query.filter_by(name=u"返点").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration)
    return 0

def getSign():
    integral = Integral.query.filter_by(name=u"注册").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration)
    return 0
def getRecomended():
    integral = Integral.query.filter_by(name=u"被推荐").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration)
    return 0
def getCarBack(fee):
    fee = int(fee)
    integral = Integral.query.filter_by(name=u"还车").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration*fee)
    return 0
def getComment():
    integral = Integral.query.filter_by(name=u"评价").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration)
    return 0
def getCommented(star):
    star = int(star)
    integral = Integral.query.filter_by(name=u"被评价").first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration*star)
    return 0
