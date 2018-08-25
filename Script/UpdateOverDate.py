from sqlalchemy import create_engine
import dbORM
import datetime as dt


def preToDate(m):
    session = dbORM.DBSession()
    if m.ordertype == "normal" and m.fromdate:
        if m.hascontinue:
            orders = session.query(dbORM.Order).filter(dbORM.Order.sourceid == m.id).all()
            countSum = 0
            for co in orders:
                countSum = countSum + co.count
            preToDate = m.fromdate + dt.timedelta(days=countSum)
        else:
            preToDate = m.fromdate + dt.timedelta(
                days=m.count)

    elif session.query(dbORM.Order).filter_by(id=m.sourceid).first() and session.query(dbORM.Order).filter(dbORM.Order.id==m.sourceid).first().fromdate:
        preToDate = dt.timedelta(
            days=m.count + session.query(dbORM.Order).filter(dbORM.Order.id==m.sourceid).first().count) + session.query(dbORM.Order).filter(
                dbORM.Order.id==m.sourceid).first().fromdate
    else:
        return None
    return preToDate



def OverDateStatus(m,ptd):
    session = dbORM.DBSession()
    try:
        preToDate = ptd
        if preToDate:
            if m.todate and m.todate > preToDate:

                return 1
            elif preToDate < dt.datetime.now():
                return 1
        return 0
    except:
        return 0


def update():
    session = dbORM.DBSession()
    orders = session.query(dbORM.Order).filter(dbORM.Order.status=="ok").limit(1000).all()
    for i in orders:
        ptd =  preToDate(i)
        ods = OverDateStatus(i,ptd)
        i.isoverdate = ods
        i.pretodate = ptd
        session.add(i)
    session.commit()
    print "update ok"
if __name__ == '__main__':
    update()
