
import dbORM

def update():
    session = dbORM.DBSession()
    orders = session.query(dbORM.Order).filter(dbORM.Order.status=="ok").filter(dbORM.Order.serverstoplocation==None).order_by(dbORM.Order.id.desc()).all()
    for i in orders:
        try:
            i.serverstoplocation = i.Serverstop.Location.name

            session.add(i)
            session.commit()
        except:
            pass
    print "update ok"
if __name__ == '__main__':
    update()