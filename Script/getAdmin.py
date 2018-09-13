# -*- coding:utf-8 -*-
from dbORM import *
def getAdmin(openid):

    user = User.query.filter_by(openid=openid).first()
    return user
def getConstruct():
    pass
def getUperAdmin(user):
    result = []
    session = DBSession()
    admins = session.query(Userrole).filter(Userrole.stage==1).first().users
    for i in admins:
        result.append(i)
    if user.Userrole.stage == 2:
        result.append(user)
    if user.Userrole.stage == 3:
        result.append(user)
        up = session.query(User).filter(User.id==user.upid).first()
        if up:
            result.append(up)
    return result
def getDownerAdmin(user):
    result = []

    if user.Userrole.stage == 1:
        admins =  User.query.all()
        for i in admins:
            result.append(i)
    if user.Userrole.stage == 2:
        result.append(user)
        downs = user.down
        for i in downs:
            result.append(i)
    if user.Userrole.stage == 3:
        result.append(user)
    return result