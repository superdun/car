# -*- coding:utf-8 -*-
from ..models.dbORM import *
def GetOrders(id):
    return Order.query.filter(Order.id==id or Order.sourceid==id).all()
def getOrderSumData(sourceOrder,cOrders):
    import datetime as dt
    from ..modules.Limit import dateCounvert
    countSum=sourceOrder.count
    priceSum = sourceOrder.totalfee
    endDateStr = u"未发车"
    overDate = u"未发车"
    for co in cOrders:
        countSum = countSum+co.count
        priceSum = priceSum+co.totalfee
    if sourceOrder.fromdate:

        if sourceOrder.todate:
            endDate = sourceOrder.fromdate + dt.timedelta(days=countSum)
            endDateStr = (endDate).strftime('%Y-%m-%d %H:%M:%S')
            overDate = (endDate - sourceOrder.todate).seconds / 60
        else:
            endDate = sourceOrder.fromdate + dt.timedelta(days=countSum)
            endDateStr = (endDate).strftime('%Y-%m-%d %H:%M:%S')
            overDate = (endDate - datetime.now()).seconds / 60
    return {"priceSum":priceSum,"countSum":countSum,"endDate":endDateStr,"overDate":overDate}
