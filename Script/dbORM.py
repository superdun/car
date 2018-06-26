# -*- coding:utf-8 -*-
from sqlalchemy import Column, String, Integer,DateTime,create_engine,ForeignKey
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from config import *
from datetime import datetime
Base = declarative_base()

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