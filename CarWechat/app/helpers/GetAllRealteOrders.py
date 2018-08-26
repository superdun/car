# -*- coding:utf-8 -*-
from ..models.dbORM import *
def GetOrders(id):
    return Order.query.filter(Order.id==id or Order.sourceid==id).all()
def GetMasterOrder(id):
    return Order.query.filter_by(id=id ).first()
def getOrderSumData(sourceOrder,cOrders):


    countSum=sourceOrder.count
    priceSum = sourceOrder.totalfee
    endDateStr = u"未发车"
    overDate = u"未发车"
    isOver = ""
    for co in cOrders:
        countSum = countSum+co.count
        priceSum = priceSum+co.totalfee
    import datetime as dtt
    if sourceOrder.fromdate:
        endDate = sourceOrder.fromdate + dtt.timedelta(days=countSum)
        endDateStr = (endDate).strftime('%Y-%m-%d %H:%M:%S')

        if sourceOrder.todate:
            actDate = sourceOrder.todate.replace(microsecond=0)
        else:
            actDate = datetime.now().replace(microsecond=0)

        if endDate>actDate:
            overDate = (endDate - actDate).seconds / 60
            isOver = "-"
        else:
            overDate = (actDate - endDate).seconds / 60
            isOver = "+"
    return {"priceSum":priceSum,"countSum":countSum,"endDate":endDateStr,"overDate":overDate,"isOver":isOver}
