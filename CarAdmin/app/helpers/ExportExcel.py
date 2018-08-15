import xlwt
from ..models.dbORM import *
import datetime

def getToday():
    today=datetime.date.today()

    return today
def getYesterday():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return yesterday
def getLastMonth():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return yesterday
def GetOrderExcelByDateRange(fromDate,toDate):
    fromDate = getYesterday()
    toDate = getToday
    orders = Order.query.filter_by(status="ok").filter(Order.created_at.between(fromDate,toDate)).all()
