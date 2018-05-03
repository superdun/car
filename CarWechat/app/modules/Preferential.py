from ..models.dbORM import *
import datetime
from datetime import datetime as dtt
from .Limit import dateCounvert
def checkWeekDay(prefer,book_at,count):
    isWeekend = False
    for i in range(count+1):
        tmpDT = book_at + datetime.timedelta(days=i)
        if tmpDT.weekday() in (5, 6):
            isWeekend = True
    if not prefer.weekend and not prefer.weekday:
        return True
    if prefer.weekend == 1 and isWeekend:
        return True
    if prefer.weekday == 1 and not isWeekend:
        return True
    return False

def checkDateRange(prefer,book_at,count):
    if prefer.start_at and  prefer.end_at:
        for i in range(count + 1):
            tmpDT = book_at + datetime.timedelta(days=i)
            if tmpDT >= prefer.start_at or tmpDT <= prefer.end_at:
                return True
    else:
        return True
    return False

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
    for prefer in prefers:
        hasCurrentPrefer = False
        if prefer:
            if prefer.status == "normal" and checkOldUser(openid,prefer) and checkWeekDay(prefer,book_at,count) and checkDateRange(prefer,book_at,count):

                if prefer.mincount and not prefer.cutfee :
                    if count >= prefer.mincount:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = ct.price
                        if prefer.multicount == 1:
                            cutfee = cutfee * count
                        if prefer.maxcutfee:
                            if cutfee > prefer.maxcutfee:
                                cutfee = prefer.maxcutfee
                        newfee = newfee - cutfee
                        if newfee < 0:
                            newfee = 0
                if prefer.discount:
                    if prefer.multicount == 1:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = newfee * (1.0 - prefer.discount)
                        newfee = newfee - cutfee
                        if newfee < 0:
                            newfee = 0
                    else:
                        isprefer = True
                        hasCurrentPrefer = True
                        cutfee = ct.price * (1.0 - prefer.discount)
                        newfee = newfee - cutfee
                        if newfee < 0:
                            newfee = 0

            if hasCurrentPrefer:
                preferName = preferName+"\n"+prefer.name
                preferId.append(prefer.id)


    if isprefer:
        cutfee = int(round(cutfee))
        newfee = totalFee-cutfee
        return {"name": preferName, 'preferid': preferId, "oldfee": totalFee, "cutfee": cutfee,
                "newfee": newfee, 'isprefer': True}

    else:
        return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee, 'isprefer': False}
