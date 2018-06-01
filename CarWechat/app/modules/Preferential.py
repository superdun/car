from ..models.dbORM import *
import datetime
from datetime import datetime as dtt
from .Limit import dateCounvert
def checkWeekDay(prefer,book_at,count):
    isWeekend = False
    isWeekDay = False
    for i in range(1,count+1):
        tmpDT = book_at + datetime.timedelta(days=i)
        if tmpDT.weekday() in (4, 5, 6):
            isWeekend = True
        else:
            isWeekDay = True
    if not prefer.weekend and not prefer.weekday:
        return True
    if prefer.weekend == 1 and isWeekend:
        return True
    if prefer.weekday == 1 and isWeekDay:
        return True
    return False

def checkDateRange(prefer,book_at,count):
    if prefer.start_at and  prefer.end_at:
        for i in range(0,count + 1):
            tmpDT = book_at + datetime.timedelta(days=i)
            if tmpDT >= prefer.start_at and tmpDT <= prefer.end_at:
                return True
    else:
        return True
    return False
def getDayCount(prefer,book_at,count):
    result = {"weekday":0,"weekend":0}
    for i in range(1,count+1):
        tmpDT = book_at + datetime.timedelta(days=i)
        if tmpDT.weekday() in (5, 6):
            result['weekend'] = result['weekend']+1
        else:
            result['weekday'] = result['weekday'] + 1
    return result
def checkOldUser(openid,prefer):
    isOld = False
    customer = Customer.query.filter_by(openid=openid).first()
    if customer:
        if customer.olduser == 1:
            isOld = True
    if  prefer.justnew == 1 and isOld:
        return False
    else:
        return True
def getFees(cartypeId, count, totalFee, openid,book_at):
    count = int(count)
    totalFee = int(totalFee)
    cartypeId = int(cartypeId)
    if book_at=="":
        book_at=dtt.now()
    else:
        book_at=dateCounvert(book_at)
    ct = Cartype.query.filter_by(id=cartypeId).first()
    prefers = ct.preferentials.order_by(Preferential.prior.desc())

    cutfee = 0
    newfee = totalFee
    isprefer = False
    preferName = ""
    preferId = []
    tmpprice = ct.price
    for prefer in prefers:

        hasCurrentPrefer = False
        if prefer:
            if prefer.status == "normal" and checkOldUser(openid,prefer) and checkWeekDay(prefer,book_at,count) and checkDateRange(prefer,book_at,count):
                days = getDayCount(prefer,book_at,count)
                if prefer.mincount and not prefer.cutfee :
                    if count >= prefer.mincount:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = cutfee+tmpprice
                        if prefer.multicount == 1:
                            cutfee = cutfee+cutfee * count
                        if prefer.maxcutfee:
                            if cutfee > prefer.maxcutfee:
                                cutfee = prefer.maxcutfee

                if  prefer.cutfee :
                    isprefer = True
                    hasCurrentPrefer = True
                    cutfee = cutfee + prefer.cutfee
                    if prefer.maxcutfee:
                        if cutfee > prefer.maxcutfee:
                            cutfee = prefer.maxcutfee

                if prefer.newpricecut:
                    tmpprice = ct.price-prefer.newpricecut

                    if prefer.multicount == 1:
                        isprefer = True
                        hasCurrentPrefer = True
                        if prefer.weekend==1:
                            cutfee = cutfee+prefer.newpricecut*days["weekend"]
                        else:
                            cutfee = cutfee+prefer.newpricecut * days["weekday"]

                if prefer.discount:
                    if prefer.multicount == 1:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = cutfee+newfee * (1.0 - prefer.discount)

                    else:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = cutfee+tmpprice * (1.0 - prefer.discount)


            if hasCurrentPrefer:
                preferName = preferName+"\n"+prefer.name
                preferId.append(prefer.id)


    if isprefer:
        cutfee = int(round(cutfee))
        newfee = totalFee-cutfee
        if newfee <= 0:
            newfee = 0
            cutfee = totalFee
        return {"name": preferName, 'preferid': preferId, "oldfee": totalFee, "cutfee": cutfee,
                "newfee": newfee, 'isprefer': True}

    else:
        return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee, 'isprefer': False}
