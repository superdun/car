# -*- coding:utf-8 -*-
import os, sys
from  flask import Blueprint, request, render_template, current_app, url_for, jsonify
from flask_login import login_required, current_user

from ..models.dbORM import *

from wechatpy.exceptions import (
    InvalidSignatureException,
    WeChatPayException
)
from datetime import datetime

from app import db

agentapi = Blueprint('agentapi', __name__)


@agentapi.route('/depart', methods=['POST'])
def departApi():
    depart_time = request.form.get("depart_time")
    oilbefore = request.form.get("oilbefore")
    contractid = request.form.get("contractId")
    outprovince = request.form.get("isOutProvince")
    carid = request.form.get("carid")
    orderid = request.form.get("orderid")
    kmbefore = request.form.get("kmbefore")
    if not depart_time:
        depart_time = datetime.now()
    else:
        from ..modules.Limit import dateCounvert
        depart_time = dateCounvert(depart_time)
    if not carid or not contractid or not oilbefore or not outprovince or not kmbefore:
        return jsonify({"status": "lacked"})
    carid = int(carid)
    orderid = int(orderid)
    try:
        import AgentWeb
        user = AgentWeb.getAdmin(current_user.openid)
    except:
        return jsonify({"status": "error"})
    order = Order.query.filter_by(id=orderid).first()
    if current_user.is_authenticated and user and order:
        admins = AgentWeb.getDownerAdmin(user)
        if order.Serverstop.userid not in ([x.id for x in admins]):
            return jsonify({"status": "error"})
        order.fromdate = depart_time
        order.oilbefore = oilbefore
        order.outprovince = outprovince
        order.contractid = contractid
        order.currentcarid = carid
        order.kmbefore = kmbefore
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"})


@agentapi.route('/back', methods=['POST'])
def backApi():
    back_time = request.form.get("back_time")
    oilafter = request.form.get("oilafter")
    isaccident = request.form.get("isaccident")
    carid = request.form.get("carid")
    orderid = request.form.get("orderid")
    kmafter = request.form.get("kmafter")
    if not back_time:
        back_time = datetime.now()
    else:
        from ..modules.Limit import dateCounvert
        back_time = dateCounvert(back_time)
    if not carid or not oilafter or not isaccident or not kmafter:
        return jsonify({"status": "lacked"})
    carid = int(carid)
    orderid = int(orderid)
    try:
        import AgentWeb
        user = AgentWeb.getAdmin(current_user.openid)
    except:
        return jsonify({"status": "error"})
    order = Order.query.filter_by(id=orderid).first()
    if current_user.is_authenticated and user and order:
        admins = AgentWeb.getDownerAdmin(user)
        if order.Serverstop.userid not in ([x.id for x in admins]):
            return jsonify({"status": "error"})
        order.todate = back_time
        order.oilafter = oilafter

        order.currentcarid = carid
        order.kmafter = kmafter
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"})
