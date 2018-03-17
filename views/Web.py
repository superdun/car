# -*- coding:utf-8 -*-
from  flask import Blueprint, render_template
from flask_login import login_required
from db.dbORM import *

web = Blueprint('web', __name__)
QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')


@web.route('/')
@login_required
def carIndex():
    return render_template('car/index.html', imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/car/<id>')
@login_required
def carDetail(id):
    data = Car.query.filter_by(id=int(id)).first()
    return render_template('car/carDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/car')
@login_required
def carList():
    data = Car.query.all()
    return render_template('car/carList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/history/<id>')
@login_required
def historyDetail(id):
    data = History.query.filter_by(id=int(id)).first()
    return render_template('car/historyDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/history')
@login_required
def historyList():
    data = History.query.all()
    return render_template('car/historyList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/mendHistory/<id>')
@login_required
def mendHistoryDetail(id):
    data = Mendhistory.query.filter_by(id=int(id)).first()
    return render_template('car/mendHistoryDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/mendHistory')
@login_required
def mendHistoryList():
    data = Mendhistory.query.all()
    return render_template('car/mendHistoryList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/customer/<id>')
@login_required
def customerDetail(id):
    data = Customer.query.filter_by(id=int(id)).first()
    return render_template('car/customerDetail.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/customer')
@login_required
def customerList():
    data = Customer.query.all()
    return render_template('car/customerList.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)


@web.route('/carRec/<id>')
@login_required
def carRec(id):
    data = Car.query.filter_by(id=int(id)).first()

    return render_template('car/carRec.html', data=data, imgDomain="http://%s" % QINIU_DOMAIN)
