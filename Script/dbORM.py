# -*- coding:utf-8 -*-
from sqlalchemy import Column, String, Integer,DateTime,create_engine,ForeignKey
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from config import *
from datetime import datetime
Base = declarative_base()


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    totalfee = Column(Integer)
    tradetype = Column(String(80))
    detail = Column(String(800))
    tradeno = Column(String(80))
    count = Column(Integer)
    status = Column(String(80), default='pending')
    prepayid = Column(String(80))
    wxtradeno = Column(String(80))
    pay_at = Column(String(80))
    isrefund = Column(Integer)
    r_pay_at = Column(String(80))
    r_tradeno = Column(String(80))
    r_wxtradeno = Column(String(80))
    r_detail = Column(String(800))
    r_totalfee = Column(Integer)
    fromdate = Column(DateTime)
    todate = Column(DateTime)
    offlinefee = Column(Integer)
    preferentialdetail = Column(String(800))
    cutfee = Column(Integer)
    oldfee = Column(Integer)
    location = Column(String(800))
    proofimg = Column(String(800))
    carbeforeimg = Column(String(800))
    carendimg = Column(String(800))
    carfee = Column(Integer)
    insurefee = Column(Integer)
    book_at = Column(String(800))
    oilbefore = Column(Integer)
    oilafter = Column(Integer)
    outprovince = Column(Integer)
    contractid = Column(String(800))
    kmbefore = Column(String(800))
    kmafter = Column(String(800))
    orderstatus = Column(String(800))
    ordertype = Column(String(800))
    sourceid = Column(Integer)
    hascontinue = Column(Integer, default=0)
    integralfee = Column(Integer)
    integtalused = Column(Integer)
    star = Column(Integer)
    isoverdate = Column(Integer)
    pretodate = Column(DateTime)
    serverstopid = Column(Integer, ForeignKey('serverstop.id'))
    customeropenid = Column(Integer, ForeignKey('customer.openid'))
    currentcarid = Column(Integer, ForeignKey('car.id'))
    serverstoplocation =  Column(String(800))
    notystatus = Column(Integer)

    def __repr__(self):
        return self.tradeno

class Serverstop(Base):
    __tablename__ = "serverstop"
    id = Column(Integer, primary_key=True)
    name =Column(String(80))
    phone = Column(String(80))
    owner = Column(String(80))
    orders = relationship('Order', backref='Serverstop', lazy='dynamic')
    userid = Column(Integer, ForeignKey('user.id'))
    locationid = Column(Integer, ForeignKey('location.id'))

    def __repr__(self):
        return self.name
class Location(Base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    name =Column(String(80))
    serrverstops = relationship('Serverstop', backref='Location', lazy='dynamic')
    def __repr__(self):
        return self.name
class Gps(Base):
    __tablename__="gps"
    id = Column(Integer, primary_key=True)
    code = Column(String(120))
    cars = relationship('Car', backref='Gps', lazy='dynamic')

    def __repr__(self):
        return self.code
class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    name = Column(String(80))
    idcode = Column(String(80), unique=True)
    gender = Column(String(80))
    comment = Column(String(800))
    img = Column(String(800))
    openid = Column(String(800), unique=True)
    password = Column(String(800))
    driveage = Column(Integer)
    phone = Column(String(800), unique=True)
    status = Column(String(800), default="pending")
    olduser =  Column(Integer, default=0)
    integral = Column(Integer, default=0)
    orders = relationship('Order', backref='Customer', lazy='dynamic')
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    name = Column(String(80))
    password = Column(String(80))
    auth = Column(Integer)
    openid = Column(String(80))
    phone = Column(String(80))
    serverstop = relationship('Serverstop', backref='User', lazy='dynamic')
    def __repr__(self):
        return self.name


class Car(Base):
    __tablename__="car"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    name = Column(String(80))
    buy_at = Column(DateTime, default=datetime.now())
    img = Column(String(200))
    orders = relationship('Order', backref='Car', lazy='dynamic')
    gpsid = Column(Integer, ForeignKey('gps.id'))

    def __repr__(self):
        return self.name




# POST

engine = create_engine(SQLALCHEMY_DATABASE_URI)

DBSession = sessionmaker(bind=engine)