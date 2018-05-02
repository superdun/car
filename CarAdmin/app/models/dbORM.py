# -*- coding:utf-8 -*-
from flask import current_app
from datetime import datetime

from app import db


class Cartypeprefer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartypeid = db.Column(db.Integer, db.ForeignKey('cartype.id'))
    preferentialid = db.Column(db.Integer, db.ForeignKey('preferential.id'))
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
    def __repr__(self):
        return self.name

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
    preferentialid = db.Column(db.Integer, db.ForeignKey('preferential.id'))
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
    orders = db.relationship('Order', backref='Preferential', lazy='dynamic')
    discount = db.Column(db.Float)
    justnew = db.Column(db.Integer)
    prior = db.Column(db.Integer)
    weekday = db.Column(db.Integer)
    weekend = db.Column(db.Integer)

    def __repr__(self):
        return self.name
class Insure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    detail = db.Column(db.String(8000))
    price = db.Column(db.Integer)
    orders = db.relationship('Order', backref='Insure', lazy='dynamic')

    def __repr__(self):
        return self.name

class Userrole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    stage = db.Column(db.Integer)
    loginrecords = db.relationship('User', backref='Userrole', lazy='dynamic')

    def __repr__(self):
        return self.name

# POST
