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
@login_required
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
        order.orderstatus = "depart"
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"})


@agentapi.route('/back', methods=['POST'])
@login_required
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
    cartype = order.Cartype
    cartype.count = cartype.count+1
    if current_user.is_authenticated and user and order:
        admins = AgentWeb.getDownerAdmin(user)
        if order.Serverstop.userid not in ([x.id for x in admins]):
            return jsonify({"status": "error"})
        order.todate = back_time
        order.oilafter = oilafter

        order.currentcarid = carid
        order.kmafter = kmafter
        order.orderstatus = "finish"
        db.session.add(order)
        db.session.add(cartype)

        db.session.commit()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error"})


@agentapi.route('/accident', methods=['POST'])
@login_required
def accidentApi():
    carid = request.form.get("carid")
    created_at = request.form.get("created_at")
    theircarcode = request.form.get("theircarcode")
    isureaompany = request.form.get("isureaompany")
    isureprice = request.form.get("isureprice")
    theirprice = request.form.get("theirprice")
    repaircompany = request.form.get("repaircompany")
    orderid = request.form.get("orderid")
    if not created_at:
        created_at = datetime.now()
    else:
        from ..modules.Limit import dateCounvert
        created_at = dateCounvert(created_at)
    if not carid   :
        return jsonify({"status": "lacked"})

    carid = int(carid)
    iorderid = None
    iisureprice=None
    itheirprice=None
    try:
        if orderid:
            iorderid = int(orderid)
        if isureprice:
            iisureprice = float(isureprice)
        if theirprice:
            itheirprice = float(theirprice)

        import AgentWeb
        user = AgentWeb.getAdmin(current_user.openid)
    except:
        return jsonify({"status": "error"})
    if request.args.get("id"):
        accident = Accident.query.filter_by(id = request.args.get("id")).first()
        accident.carid = carid
        accident.created_at =created_at
        accident.created_at = created_at
        accident.theircarcode = theircarcode
        accident.isureaompany = isureaompany
        accident.isureprice = iisureprice
        accident.theirprice = itheirprice
        accident.repaircompany = repaircompany
        accident.orderid = iorderid
        accident.userid = user.id
    else:
        accident = Accident(carid=carid, created_at=created_at, theircarcode=theircarcode, isureaompany=isureaompany,
                        isureprice=iisureprice,theirprice=itheirprice,repaircompany=repaircompany,orderid=iorderid,userid=user.id)
    db.session.add(accident)
    db.session.commit()
    return jsonify({"status": "ok"})



@agentapi.route('/move', methods=['POST'])
@login_required
def moveApi():
    carid = request.form.get("carid")
    created_at = request.form.get("created_at")
    fromid = request.form.get("fromid")
    toid = request.form.get("toid")
    fromkm = request.form.get("fromkm")
    tokm = request.form.get("tokm")

    if not created_at:
        created_at = datetime.now()
    else:
        from ..modules.Limit import dateCounvert
        created_at = dateCounvert(created_at)
    if not carid or not fromid or not fromkm :
        return jsonify({"status": "lacked"})

    carid = int(carid)
    fromid = int(fromid)

    fromkm = int(fromkm)

    try:
        toid = int(toid)
        tokm = int(tokm)
    except:
        toid = tokm = None
    try:
        import AgentWeb
        user = AgentWeb.getAdmin(current_user.openid)
    except:
        return jsonify({"status": "error"})
    if request.args.get("id"):
        move = Move.query.filter_by(id = request.args.get("id")).first()
        move.carid = carid
        move.created_at = created_at
        move.fromid = fromid
        move.toid = toid
        move.fromkm = fromkm
        move.tokm = tokm
        move.userid = user.id


    else:
        move = Move(carid=carid, created_at=created_at, fromid=fromid, toid=toid,
                    fromkm=fromkm,tokm=tokm,userid=user.id)
    db.session.add(move)
    db.session.commit()
    return jsonify({"status": "ok"})

@agentapi.route('/apply', methods=['POST'])
@login_required
def applyApi():
    carid = request.form.get("carid")
    created_at = request.form.get("created_at")
    comment = request.form.get("comment")


    if not created_at:
        created_at = datetime.now()
    else:
        from ..modules.Limit import dateCounvert
        created_at = dateCounvert(created_at)
    if not carid or not comment :
        return jsonify({"status": "lacked"})

    carid = int(carid)

    try:
        import AgentWeb
        user = AgentWeb.getAdmin(current_user.openid)
    except:
        return jsonify({"status": "error"})

    apply = Apply(carid=carid, created_at=created_at, comment=comment,userid=user.id)
    db.session.add(apply)
    db.session.commit()
    return jsonify({"status": "ok"})

@agentapi.route('/carsbycartype', methods=['POST'])
@login_required
def carsbycartypeApi():
    cartypeid = request.form.get("cartypeid")
    if not cartypeid:
        return jsonify([])

    cars = Cartype.query.filter_by(id=cartypeid).first().cars
    result = []
    for i in cars:
        result.append({'value':i.id,'label':i.name})
    return jsonify(result)
