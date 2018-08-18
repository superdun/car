import datetime


def getToday():
    today = datetime.date.today()

    return today


def getToweek():
    today = datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)
    last_week_start = today - datetime.timedelta(days=today.weekday())
    return [last_week_start, today]


def getTomonth():
    today = datetime.date.today()
    this_month_start = datetime.datetime(today.year, today.month, 1)
    return [this_month_start, today]


def getLastYesterdayRange():
    today = datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return [yesterday, today]


def getDayRange(count):
    today = datetime.date.today() - datetime.timedelta(days=count - 1)
    today = datetime.datetime(today.year, today.month, today.day)
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return [yesterday, today]


def getLastWeekRange():
    today = datetime.date.today()
    today = datetime.datetime(today.year, today.month, today.day)
    last_week_start = today - datetime.timedelta(days=today.weekday() + 7)
    last_week_end = today - datetime.timedelta(days=today.weekday() + 1)
    return [last_week_start, last_week_end]


def getWeekRange(count):
    if count == 0:
        return getToweek()
    today = datetime.date.today() - datetime.timedelta(weeks=count - 1)
    today = datetime.datetime(today.year, today.month, today.day)
    last_week_start = today - datetime.timedelta(days=today.weekday() + 7)
    last_week_end = today - datetime.timedelta(days=today.weekday() + 1)
    return [last_week_start, last_week_end]


def getLastMonthRange():
    today = datetime.date.today()
    this_month_start = datetime.datetime(today.year, today.month, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    return [last_month_start, last_month_end]


def getMonthRange(count):
    if count == 0:
        return getTomonth()
    today = datetime.date.today()
    this_month_start = datetime.datetime(today.year, today.month + 1 - count, 1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
    return [last_month_start, last_month_end]

# def GetOrderExcelByDateRange(fromDate,toDate):
#     fromDate = getYesterday()
#     toDate = getToday
#     orders = Order.query.filter_by(status="ok").filter(Order.created_at.between(fromDate,toDate)).all()
