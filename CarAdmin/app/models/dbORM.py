# -*- coding:utf-8 -*-
from flask import current_app
from datetime import datetime
import datetime as dt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select,func
from app import db


class Cartypeprefer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartypeid = db.Column(db.Integer, db.ForeignKey('cartype.id'))
    preferentialid = db.Column(db.Integer, db.ForeignKey('preferential.id'))
    def __repr__(self):
        return self.id

class Insurecartype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartypeid = db.Column(db.Integer, db.ForeignKey('cartype.id'))
    insureid = db.Column(db.Integer, db.ForeignKey('insure.id'))
    def __repr__(self):
        return self.id
class Cartype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(80))
    price = db.Column(db.String(80))
    cars = db.relationship('Car', backref='Cartype', lazy='dynamic')
    img = db.Column(db.String(200))
    status = db.Column(db.String(800), default="pending")
    orders = db.relationship('Order', backref='Cartype', lazy='dynamic')
    preferentials = db.relationship("Preferential" , secondary="cartypeprefer", backref='Cartype', lazy='dynamic')
    carcatid = db.Column(db.Integer, db.ForeignKey('carcat.id'))
    count = db.Column(db.Integer)
    limitid = db.Column(db.Integer, db.ForeignKey('limit.id'))
    insures = db.relationship("Insure", secondary="insurecartype", backref='Cartype', lazy='dynamic')

    @hybrid_property
    def remind_count(self):
        # return len(self.cars)   # @note: use when non-dynamic relationship
        return Car.query.filter(Car.typeid==self.id).filter(Car.status=="normal").count()  # @note: use when dynamic relationship

    @hybrid_property
    def rent_count(self):
        # return len(self.cars)   # @note: use when non-dynamic relationship
        return Car.query.filter(Car.typeid==self.id).filter(Car.status=="pending").count()  # @note: use when dynamic relationship

    def __repr__(self):
        return u"%s,单价%s元" % (self.name, float(self.price) / 100)

class Limit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    name = db.Column(db.String(800))
    mincount = db.Column(db.Integer)
    maxcount = db.Column(db.Integer)
    cartypes = db.relationship('Cartype', backref='Limit', lazy='dynamic')

    def __repr__(self):
        return self.name

class Gps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(120))
    cars = db.relationship('Car', backref='Gps', lazy='dynamic')

    def __repr__(self):
        return self.code


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(80))
    buy_at = db.Column(db.DateTime, default=datetime.now())
    img = db.Column(db.String(200))
    gpsid = db.Column(db.Integer, db.ForeignKey('gps.id'))
    typeid = db.Column(db.Integer, db.ForeignKey('cartype.id'))
    histories = db.relationship('History', backref='Car', lazy='dynamic')
    mendhistories = db.relationship('Mendhistory', backref='Car', lazy='dynamic')
    status = db.Column(db.String(80), default="pending")
    orders = db.relationship('Order', backref='Car', lazy='dynamic')
    accidents = db.relationship('Accident', backref='Car', lazy='dynamic')
    moves = db.relationship('Move', backref='Car', lazy='dynamic')
    applies = db.relationship('Apply', backref='Car', lazy='dynamic')

    def __repr__(self):
        return self.name


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(80))
    idcode = db.Column(db.String(80), unique=True)
    gender = db.Column(db.String(80))
    comment = db.Column(db.String(800))
    img = db.Column(db.String(800))
    histories = db.relationship('History', backref='Customer', lazy='dynamic')
    orders = db.relationship('Order', backref='Customer', lazy='dynamic')
    openid = db.Column(db.String(800), unique=True)
    password = db.Column(db.String(800))
    driveage = db.Column(db.Integer)
    phone = db.Column(db.String(800), unique=True)
    status = db.Column(db.String(800), default="pending")
    olduser =  db.Column(db.Integer, default=0)
    integral = db.Column(db.Integer, default=0)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return ""


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    started_at = db.Column(db.DateTime, default=datetime.now())
    ended_at = db.Column(db.DateTime, default=datetime.now())
    customerid = db.Column(db.Integer, db.ForeignKey('customer.id'))
    carid = db.Column(db.Integer, db.ForeignKey('car.id'))
    type = db.Column(db.String(80))
    price = db.Column(db.String(80))
    status = db.Column(db.String(80))

    def __repr__(self):
        return "%s %s" % (self.created_at, self.type)


class Mendhistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    carid = db.Column(db.Integer, db.ForeignKey('car.id'))
    type = db.Column(db.String(80))
    price = db.Column(db.String(80))
    status = db.Column(db.String(80))
    location = db.Column(db.String(80))
    def __repr__(self):
        return "%s %s" % (self.created_at, self.type)
class Serverstop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(80))
    phone = db.Column(db.String(80))
    owner = db.Column(db.String(80))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    orders = db.relationship('Order', backref='Serverstop', lazy='dynamic')
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    mfroms = db.relationship('Move', backref='fromServerstop', lazy='dynamic',foreign_keys="Move.fromid")
    mtos = db.relationship('Move', backref='toServerstop', lazy='dynamic',foreign_keys="Move.toid")
    def __repr__(self):
        return self.name
class Hy(object):
    def __init__(self,a,b):
        self.value = a
        self.type = b
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    carid = db.Column(db.Integer, db.ForeignKey('cartype.id'))
    totalfee = db.Column(db.Integer)
    customeropenid = db.Column(db.Integer, db.ForeignKey('customer.openid'))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    tradetype = db.Column(db.String(80))
    detail = db.Column(db.String(800))
    tradeno = db.Column(db.String(80))
    count = db.Column(db.Integer)
    status = db.Column(db.String(80), default='pending')
    prepayid = db.Column(db.String(80))
    wxtradeno = db.Column(db.String(80))
    pay_at = db.Column(db.String(80))
    isrefund = db.Column(db.Integer)
    r_pay_at = db.Column(db.String(80))
    r_tradeno = db.Column(db.String(80))
    r_wxtradeno = db.Column(db.String(80))
    r_detail = db.Column(db.String(800))
    r_totalfee = db.Column(db.Integer)
    fromdate = db.Column(db.DateTime)
    todate = db.Column(db.DateTime)
    offlinefee = db.Column(db.Integer)
    preferentialdetail = db.Column(db.String(800))
    cutfee = db.Column(db.Integer)
    oldfee = db.Column(db.Integer)
    location = db.Column(db.String(800))
    currentcarid = db.Column(db.Integer, db.ForeignKey('car.id'))
    serverstopid = db.Column(db.Integer, db.ForeignKey('serverstop.id'))
    proofimg = db.Column(db.String(800))
    carbeforeimg = db.Column(db.String(800))
    carendimg = db.Column(db.String(800))
    insureid = db.Column(db.Integer, db.ForeignKey('insure.id'))

    carfee = db.Column(db.Integer)
    insurefee = db.Column(db.Integer)
    book_at = db.Column(db.String(800))
    oilbefore = db.Column(db.Integer)
    oilafter = db.Column(db.Integer)
    outprovince = db.Column(db.Integer)
    contractid = db.Column(db.String(800))
    kmbefore = db.Column(db.String(800))
    kmafter = db.Column(db.String(800))
    orderstatus = db.Column(db.String(800))
    ordertype = db.Column(db.String(800))
    sourceid = db.Column(db.Integer)
    hascontinue = db.Column(db.Integer, default=0)
    integralfee = db.Column(db.Integer)
    integtalused = db.Column(db.Integer)
    star = db.Column(db.Integer)

    @hybrid_property
    def preToDate(self):
        m = Order.query.filter_by(id=self.id).first()
        if m.ordertype == "normal" and m.fromdate:
            if m.hascontinue:
                orders = Order.query.filter(Order.sourceid == self.id).all()
                countSum=0
                for co in orders:
                    countSum = countSum + co.count
                preToDate = m.fromdate + dt.timedelta(days=countSum)
            else:
                preToDate = m.fromdate + dt.timedelta(
                    days=m.count)

        elif Order.query.filter_by(id=m.sourceid).first() and Order.query.filter_by(id=m.sourceid).first().fromdate:
            preToDate = dt.timedelta(days=m.count + Order.query.filter_by(id=m.sourceid).first().count) + Order.query.filter_by(id=m.sourceid).first().fromdate
        else:
            return None
        return preToDate

    @hybrid_property
    def OverDateStatus(self):
        preToDate = self.preToDate
        m = Order.query.filter_by(id=self.id).first()
        if preToDate:
            if m.todate and m.todate > preToDate:
                return self.id==self.id
            elif preToDate < datetime.now():
                return self.id==self.id
        return self.id!=self.id

    def __repr__(self):
        return self.tradeno


class Error(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    msg = db.Column(db.String(8000))
    type = db.Column(db.Integer)

    def __repr__(self):
        return self.id
class Carcat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8000))
    cartypes = db.relationship('Cartype', backref='Carcat', lazy='dynamic')
    def __repr__(self):
        return self.name

class Loginrecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    detail = db.Column(db.String(8000))
    ip = db.Column(db.String(80))

    def __repr__(self):
        return self.created_at


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(80))
    password = db.Column(db.String(80))
    auth = db.Column(db.Integer)
    histories = db.relationship('Mendhistory', backref='User', lazy='dynamic')
    roleid = db.Column(db.Integer, db.ForeignKey('userrole.id'))
    orders = db.relationship('Order', backref='User', lazy='dynamic')
    loginrecords = db.relationship('Loginrecord', backref='User', lazy='dynamic')
    openid = db.Column(db.String(80))
    upid = db.Column(db.Integer, db.ForeignKey('user.id'))
    down = db.relationship('User', foreign_keys=upid)
    serverstop = db.relationship('Serverstop', backref='User', lazy='dynamic')
    accidents = db.relationship('Accident', backref='User', lazy='dynamic')
    moves = db.relationship('Move', backref='User', lazy='dynamic')
    applies = db.relationship('Apply', backref='User', lazy='dynamic')
    phone = db.Column(db.String(80))
    def __repr__(self):
        return self.name


class Preferential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    mincount = db.Column(db.Integer)
    minfee = db.Column(db.Integer)
    cutfee = db.Column(db.Integer)
    multicount = db.Column(db.Integer)
    maxcutfee = db.Column(db.Integer)
    status = db.Column(db.String(80), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now())
    cartypes = db.relationship('Cartype', secondary="cartypeprefer", backref='Preferential', lazy='dynamic')
    # orders = db.relationship('Order', backref='Preferential', lazy='dynamic')
    discount = db.Column(db.Float)
    justnew = db.Column(db.Integer)
    prior = db.Column(db.Integer)
    weekday = db.Column(db.Integer)
    weekend = db.Column(db.Integer)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    newpricecut = db.Column(db.Integer)
    def __repr__(self):
        return self.name
class Insure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    detail = db.Column(db.String(8000))
    price = db.Column(db.Integer)
    orders = db.relationship('Order', backref='Insure', lazy='dynamic')
    cartypes = db.relationship("Cartype", secondary="insurecartype", backref='Insure', lazy='dynamic')
    def __repr__(self):
        return self.name

class Accident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    carid = db.Column(db.Integer, db.ForeignKey('car.id'))
    img1 = db.Column(db.String(800))
    img2 = db.Column(db.String(800))
    img3 = db.Column(db.String(800))
    img4 = db.Column(db.String(800))
    img5 = db.Column(db.String(800))
    img6 = db.Column(db.String(800))
    repaircompany = db.Column(db.String(800))
    theircarcode = db.Column(db.String(800))
    isureaompany = db.Column(db.String(800))
    isureprice = db.Column(db.Float)
    theirprice = db.Column(db.Float)
    orderid = db.Column(db.Integer, db.ForeignKey('order.id'))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return self.id

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    carid = db.Column(db.Integer, db.ForeignKey('car.id'))
    fromid = db.Column(db.Integer, db.ForeignKey('serverstop.id'))
    toid = db.Column(db.Integer, db.ForeignKey('serverstop.id'))
    fromkm = db.Column(db.Integer)
    tokm = db.Column(db.Integer)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return self.id

class Apply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    carid = db.Column(db.Integer, db.ForeignKey('car.id'))
    comment = db.Column(db.String(800))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return self.id




class Userrole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    stage = db.Column(db.Integer)
    users = db.relationship('User', backref='Userrole', lazy='dynamic')

    def __repr__(self):
        return self.name

# POST
class Integral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ration = db.Column(db.Float, default=1)
    name = db.Column(db.String(80))

    def __repr__(self):
        return self.name
