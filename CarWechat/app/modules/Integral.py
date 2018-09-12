# -*- coding:utf-8 -*-
from ..models.dbORM import *
import datetime
from datetime import datetime as dtt
from ..modules.Wechat import sendIntegralTemplateByCustomer
from math import floor,ceil
from app import db

def getIntegralCut(openid,fee):
    fee = float(fee)/100-0.1
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    integral = Integral.query.filter_by(name=u"兑现").first()
    integralThreshold = Integral.query.filter_by(name=u"满").first()
    customer = Customer.query.filter_by(openid=openid).first()
    customerIntegral = customer.integral
    if customerIntegral==0 or not integralThreshold or not integral or not customer or not integralSwitch or not int(integralSwitch.ration)==1:
        return {"cut":0,"used":0,"msg":u"积分还不够多哦"}
    else:
        ration = integral.ration
        cutSum = (floor(customerIntegral*ration*100))/100
        if cutSum<integralThreshold.ration:
            return {"cut": 0, "used": 0, "msg": u"积分还不够多哦"}
        if cutSum<fee:
            return {"cut": cutSum, "used": customerIntegral}
        else:
            return {"cut": fee, "used": int(ceil(fee/ration))}

def getIntegralImprove(fee,name):
    fee = int(fee)
    integralCash = Integral.query.filter_by(name=u"兑现").first()
    integral = Integral.query.filter_by(name=name).first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    if not integralSwitch or not integralCash or  not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration*fee/100/integralCash.ration)
    return 0
def getIntegral(name):
    integral = Integral.query.filter_by(name=name).first()
    integralSwitch = Integral.query.filter_by(name=u"开关").first()
    integralCash = Integral.query.filter_by(name=u"兑现").first()
    if not integralSwitch or not integralCash or not int(integralSwitch.ration)==1:
        return 0
    if integral:
        return int(integral.ration/integralCash.ration)
    return 0

def saveIntegeralRecord(customer,integral,detail,orderid=None,otherorderid=None):
    record = Integralrecord(customerid=customer.id,integral=integral,detail=detail,orderid=orderid,otherorderid=otherorderid,created_at = datetime.datetime.now())
    db.session.add(record)
    db.session.commit()
    sendIntegralTemplateByCustomer(customer,integral,detail)
# def getRecomend():
#
#     integral = Integral.query.filter_by(name=u"返点").first()
#     integralSwitch = Integral.query.filter_by(name=u"开关").first()
#     integralCash = Integral.query.filter_by(name=u"兑现").first()
#     if not integralSwitch or not integralCash or not int(integralSwitch.ration)==1:
#         return 0
#     if integral:
#         return int(integral.ration/integralCash.ration)
#     return 0

# def getSign():
#     integral = Integral.query.filter_by(name=u"注册").first()
#     integralSwitch = Integral.query.filter_by(name=u"开关").first()
#     integralCash = Integral.query.filter_by(name=u"兑现").first()
#     if not integralSwitch or not integralCash or not int(integralSwitch.ration)==1:
#         return 0
#     if integral:
#         return int(integral.ration/integralCash.ration)
#     return 0
# def getRecomended():
#     integral = Integral.query.filter_by(name=u"被推荐").first()
#     integralSwitch = Integral.query.filter_by(name=u"开关").first()
#     integralCash = Integral.query.filter_by(name=u"兑现").first()
#     if not integralSwitch or not integralCash or not int(integralSwitch.ration)==1:
#         return 0
#     if integral:
#         return int(integral.ration/integralCash.ration)
#     return 0
def getCarBack(fee):
    # fee = int(fee)
    # integral = Integral.query.filter_by(name=u"还车").first()
    # integralSwitch = Integral.query.filter_by(name=u"开关").first()
    # if not integralSwitch or not int(integralSwitch.ration)==1:
    #     return 0
    # if integral:
    #     return int(integral.ration*fee)
    return 0
def getComment():
    # integral = Integral.query.filter_by(name=u"评价").first()
    # integralSwitch = Integral.query.filter_by(name=u"开关").first()
    # if not integralSwitch or not int(integralSwitch.ration)==1:
    #     return 0
    # if integral:
    #     return int(integral.ration)
    return 0
def getCommented(star):
    # star = int(star)
    # integral = Integral.query.filter_by(name=u"被评价").first()
    # integralSwitch = Integral.query.filter_by(name=u"开关").first()
    # if not integralSwitch or not int(integralSwitch.ration)==1:
    #     return 0
    # if integral:
    #     return int(integral.ration*star)
    return 0
