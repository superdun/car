# -*- coding:utf-8 -*-
from ..models.dbORM import *
from sqlalchemy import func
from ..helpers.ExportExcel import getWeekRange, getMonthRange
import copy
from app import db


class getKpiClass(object):
    def __init__(self, r):
        self.weekName = (u"周一", u"周二", u"周三", u"周四", u"周五", u"周六", u"周日")
        self.monthName = (u"1月", u"2月", u"3月", u"4月", u"5月", u"6月", u"7月", u"8月", u"9月", u"10月", u"11月", u"12月")
        self.KpiResult = r

    def getOrderCount(self, c, range):
        if range == "w":
            r = getWeekRange(c)
            w = str(r[0].month) + "/" + str(r[0].day)
            rn = w

        else:
            r = getMonthRange(c)
            w = r[0].month
            rn = self.monthName[w - 1]

        return [rn, Order.query.filter(
            Order.status == "ok").filter(Order.created_at >= r[0]).filter(
            Order.created_at <= r[1]).count()]

    def getFee(self, c, range):
        if range == "w":
            r = getWeekRange(c)
            w = str(r[0].month) + "/" + str(r[0].day)
            rn = w

        else:
            r = getMonthRange(c)
            w = r[0].month
            rn = self.monthName[w - 1]
        rawResult = Order.query.with_entities(func.sum(Order.totalfee).label('sum')).filter(
            Order.status == "ok").filter(Order.created_at >= r[0]).filter(
            Order.created_at <= r[1]).first().sum
        if rawResult:
            return [rn,
                    int(str(rawResult)) / 100]
        else:
            return [rn, 0]

    def getUserCount(self, c, range):
        if range == "w":
            r = getWeekRange(c)
            w = r[0].weekday()
            rn = self.weekName[w]

        else:
            r = getMonthRange(c)
            w = r[0].month
            rn = self.monthName[w - 1]
        return [rn, int(
            Order.query.with_entities(func.sum(Order.totalfee).label('sum')).filter(Order.status == "ok").filter(
                Order.created_at >= r[0]).filter(
                Order.created_at <= r[1]).first().sum)]

    def getAgentFee(self, range):
        if range == "w":
            r = getWeekRange(1)
            rn = u"上周"

        else:
            r = getMonthRange(1)
            w = r[0].month
            rn = self.monthName[w]
        rawResult = db.session.query(Order.serverstopid, func.sum(Order.totalfee).label('sum')).filter(
            Order.status == "ok").filter(
                Order.created_at >= r[0]).filter(
                Order.created_at <= r[1]).group_by(Order.serverstopid).all()
        results = []
        nameResults = []
        for i in rawResult:
            result = {"value": 0, "name": ""}
            st = Serverstop.query.filter_by(id=i[0]).first()
            if st:
                result["name"] = st.name

            else:
                result["name"] = u'位置服务站'
            result["value"] = int(i[1])
            nameResults.append(result["name"])
            results.append(result)
        return [rn, results, nameResults]

    def setOption(self, target, color, title, name):
        self.KpiResult[target]["color"] = [color]
        self.KpiResult[target]["title"]["text"] = title
        self.KpiResult[target]["legend"]["data"] = [name]
        self.KpiResult[target]["series"][0]["name"] = name

    def setPieOption(self, target, title):
        self.KpiResult[target]["title"]["text"] = title

    def setOptionData(self, target, data):
        self.KpiResult[target]["series"][0]["data"].append(data[1])
        self.KpiResult[target]["xAxis"]["data"].append(data[0])

    def setPieOptionData(self, target, data):
        self.KpiResult[target]["title"]["text"] = data[0] + " " + self.KpiResult[target]["title"]["text"]
        self.KpiResult[target]["series"][0]["data"] = data[1]
        # self.KpiResult[target]["legend"]["data"] = data[2]


def getOrderSumFromAdminData(data):
    result = {"oldfee": 0, "cutfee": 0, "integralfee": 0, "totalfee": 0, "count": 0, "normal": 0, "continue": 0}
    for d in data:
        result["oldfee"] = result["oldfee"] + int(d.oldfee) / 100 if d.oldfee else result["oldfee"]
        result["cutfee"] = result["cutfee"] + int(d.cutfee) / 100 if d.cutfee else result["cutfee"]
        result["integralfee"] = result["integralfee"] + int(d.integralfee) / 100 if d.integralfee else result[
            "integralfee"]
        result["totalfee"] = result["totalfee"] + int(d.totalfee) / 100 if d.totalfee else result["totalfee"]
        result["count"] = result["count"] + 1
        if d.ordertype == "normal":
            result["normal"] = result["normal"] + 1
        else:
            result["continue"] = result["continue"] + 1
    return result


def getKPIs(resultModel, optionsPieModel):
    count = 8

    KpiResult = {"orderCountMonth": copy.deepcopy(resultModel), "orderCountWeek": copy.deepcopy(resultModel),
                 "feeMonth": copy.deepcopy(resultModel), "feeWeek": copy.deepcopy(resultModel),
                 "userMonth": copy.copy(resultModel), "userWeek": copy.deepcopy(resultModel),
                 "agentMonth": copy.deepcopy(optionsPieModel), "agentWeek": copy.deepcopy(optionsPieModel)}

    getKpiObj = getKpiClass(KpiResult)
    getKpiObj.setOption("orderCountWeek", '#2ec7c9', u"按周订单数", u"订单数")
    getKpiObj.setOption("orderCountMonth", '#b6a2de', u"按月订单数", u"订单数")
    getKpiObj.setOption("feeWeek", '#5ab1ef ', u"按周收入", u"元")
    getKpiObj.setOption("feeMonth", '#ffb980', u"按月收入", u"元")
    getKpiObj.setPieOption("agentMonth", u"服务站收入情况")
    getKpiObj.setPieOption("agentWeek", u"服务站收入情况")
    for i in range(count)[::-1]:
        weekOrderCount = getKpiObj.getOrderCount(i, "w")
        monthOrderCount = getKpiObj.getOrderCount(i, "m")
        weekOrderFee = getKpiObj.getFee(i, "w")
        monthOrderFee = getKpiObj.getFee(i, "m")

        getKpiObj.setOptionData("orderCountWeek", weekOrderCount)
        getKpiObj.setOptionData("orderCountMonth", monthOrderCount)
        getKpiObj.setOptionData("feeWeek", weekOrderFee)
        getKpiObj.setOptionData("feeMonth", monthOrderFee)
    monthAgentFee = getKpiObj.getAgentFee("m")
    getKpiObj.setPieOptionData("agentMonth", monthAgentFee)
    weekAgentFee = getKpiObj.getAgentFee("w")
    getKpiObj.setPieOptionData("agentWeek", weekAgentFee)
    return getKpiObj.KpiResult
