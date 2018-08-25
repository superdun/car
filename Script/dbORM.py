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

    def __repr__(self):
        return self.tradeno
class Gps(Base):
    __tablename__="gps"
    id = Column(Integer, primary_key=True)
    code = Column(String(120))
    cars = relationship('Car', backref='Gps', lazy='dynamic')

    def __repr__(self):
        return self.code


class Car(Base):
    __tablename__="car"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    name = Column(String(80))
    buy_at = Column(DateTime, default=datetime.now())
    img = Column(String(200))
    gpsid = Column(Integer, ForeignKey('gps.id'))


    def __repr__(self):
        return self.name




# POST

engine = create_engine(SQLALCHEMY_DATABASE_URI)

DBSession = sessionmaker(bind=engine)