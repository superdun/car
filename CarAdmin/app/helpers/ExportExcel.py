# import xlwt
from ..models.dbORM import *
from sqlalchemy import func
import datetime

def getToday():
    today=datetime.date.today()

    return today
def getLastYesterdayRange():
    today=datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return [yesterday,today]
def getLastWeekRange():
    today=datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)
    last_week_start = today - datetime.timedelta(days=today.weekday() + 7)
    last_week_end = today - datetime.timedelta(days=today.weekday() + 1)
    return [last_week_start,last_week_end]
def getLastMonthRange():
    today=datetime.date.today()
    this_month_start = datetime.datetime(today.year, today.month, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    return [last_month_start,last_month_end]
# def GetOrderExcelByDateRange(fromDate,toDate):
#     fromDate = getYesterday()
#     toDate = getToday
#     orders = Order.query.filter_by(status="ok").filter(Order.created_at.between(fromDate,toDate)).all()
def getOrderSumFromAdminData(data):
    result={"oldfee":0,"cutfee":0,"integralfee":0,"totalfee":0,"count":0,"normal":0,"continue":0}
    for d in data:
        result["oldfee"] = result["oldfee"]+d.oldfee if d.oldfee.isdigit() else result["oldfee"]
        result["cutfee"] = result["cutfee"]+d.cutfee if d.cutfee.isdigit() else result["cutfee"]
        result["integralfee"] = result["integralfee"]+d.integralfee if d.integralfee.isdigit() else result["integralfee"]
        result["totalfee"] = result["totalfee"]+d.totalfee if d.totalfee.isdigit() else result["totalfee"]
        result["count"] = result["count"]+1
        if d.ordertype=="normal":
            result["normal"]=result["normal"]+1
        else:
            result["continue"]=result["continue"]+1
    return result


