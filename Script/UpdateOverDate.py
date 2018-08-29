from sqlalchemy import create_engine
import dbORM
import datetime as dt
from config import *
import SMS


def preToDate(m):
    session = dbORM.DBSession()
    if m.ordertype == "normal" and m.fromdate:
        if m.hascontinue:
            orders = session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
                dbORM.Order.sourceid == m.id).all()
            countSum = m.count
            for co in orders:
                countSum = countSum + co.count
            preToDate = m.fromdate + dt.timedelta(days=countSum)
        else:
            preToDate = m.fromdate + dt.timedelta(
                days=m.count)

    elif session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter_by(
            id=m.sourceid).first() and session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
                    dbORM.Order.id == m.sourceid).first().fromdate:
        preToDate = dt.timedelta(
            days=m.count + session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
                dbORM.Order.id == m.sourceid).first().count) + session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
            dbORM.Order.id == m.sourceid).first().fromdate
    else:
        return None
    return preToDate


def OverDateStatus(m, ptd):
    session = dbORM.DBSession()
    try:
        preToDate = ptd
        if preToDate:
            if m.ordertype == "normal":
                if m.todate:
                    if m.todate > preToDate:
                        return 1

                elif preToDate < dt.datetime.now():
                    return 1
            elif m.ordertype == "continue" and m.sourceid:
                masterOrder = session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
                    dbORM.Order.id == m.sourceid).first()
                if masterOrder:
                    if masterOrder.todate:
                        if masterOrder.todate > preToDate:
                            return 1

                    elif preToDate < dt.datetime.now():
                        return 1
        return 0
    except:
        return 0


def noty(session, order):
    pass
    # if not order.todate and  order.notystatus==0:
    #     cnum = order.Customer.phone
    #     openid = order.Serverstop.User.openid
    #     user = session.query(dbORM.Customer).filter(dbORM.Customer.openid == openid).first()
    #     unum=""
    #     if user:
    #         unum = user.phone
    #     msg = '{"carname": "%s"}' % (order.Car.name)
    #     if cnum:
    #         sendResultC = SMS.sendSMS('back', cnum, msg.decode('utf8')).send()
    #     if unum:
    #         sendResultU = SMS.sendSMS('back', cnum, msg.decode('utf8')).send()


def update():
    session = dbORM.DBSession()
    lastMonth = dt.datetime.now() - dt.timedelta(weeks=4)
    orders = session.query(dbORM.Order).filter(dbORM.Order.status == "ok").filter(
        dbORM.Order.created_at > lastMonth).order_by(dbORM.Order.id.desc()).limit(1000).all()
    for i in orders:
        print i.id
        ptd = preToDate(i)
        ods = OverDateStatus(i, ptd)
        if ods == 1:
            noty(session, i)
        if i.isoverdate != ods or i.pretodate != ptd:
            i.isoverdate = ods

            i.pretodate = ptd
            session.add(i)
            session.commit()
    print "update ok"


if __name__ == '__main__':
    update()
