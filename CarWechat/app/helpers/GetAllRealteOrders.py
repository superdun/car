# -*- coding:utf-8 -*-
from ..models.dbORM import *
def GetOrders(id):
    return Order.query.filter(Order.id==id or Order.sourceid==id).all()
def getOrderSumData(sourceOrder,cOrders):
    countSum=sourceOrder.count
    priceSum = sourceOrder.totalfee
    for co in cOrders:
        countSum = countSum+co.count
        priceSum = priceSum+co.totalfee
    return {"priceSum":priceSum,"countSum":countSum}
