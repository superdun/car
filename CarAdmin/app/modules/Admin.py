# -*- coding: utf-8 -*-
from flask import request, redirect, url_for
import os
import os.path as op
import time
from flask_admin import Admin, form, expose, AdminIndexView
import flask_login
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import IntEqualFilter
from flask_admin.contrib.sqla.view import func
from jinja2 import Markup
from flask import current_app
from ..models.dbORM import *
from ..helpers import thumb
from flask_qiniustorage import Qiniu
from wtforms import SelectField, PasswordField
import hashlib
import datetime
from ..helpers.GetAllRealteOrders import GetMasterOrder, GetContinueOrders, getOrderSumData
from ..helpers.ExportExcel import getLastMonthRange, getLastWeekRange, getLastYesterdayRange
from ..modules.KPI import getOrderSumFromAdminData
from ..helpers.dateHelper import dateStringMakerForFilter
import json
from app import db


def getQiniuDomain():
    return current_app.config.get('QINIU_BUCKET_DOMAIN', '')


def getUploadUrl():
    return current_app.config.get('UPLOAD_URL')


def date_format(value):
    return time.strftime(u'%Y/%m/%d %H:%M:%S', time.localtime(float(value)))


def img_url_format(value):
    return Markup("<img src='%s'>" % ("http://" + getQiniuDomain() + value))


def dashboard():
    admin = Admin(current_app, name=u'通力后台管理', index_view=KPIView())
    admin.add_view(UserView(User, db.session, name=u"员工管理"))
    admin.add_view(UserView1(User, db.session, name=u"个人资料", endpoint="profile"))
    admin.add_view(CarView(Car, db.session, name=u"车辆管理"))
    admin.add_view(GpsView(Gps, db.session, name=u"设备管理"))
    admin.add_view(PreferentialView(Preferential, db.session, name=u"优惠管理"))
    admin.add_view(CustomerView(Customer, db.session, name=u"客户管理"))
    admin.add_view(CartypeView(Cartype, db.session, name=u"车型管理"))
    admin.add_view(OrderView(Order, db.session, name=u"订单管理"))
    admin.add_view(OrderView1(Order, db.session, name=u"我的订单", endpoint="myorders"))
    admin.add_view(CarcatView(Carcat, db.session, name=u"车类管理"))
    admin.add_view(ServerstopView(Serverstop, db.session, name=u"服务站管理"))
    admin.add_view(LocationView(Location, db.session, name=u"地区"))
    # admin.add_view(OrderAdminView(name=u'订单管理', endpoint='refund'))
    admin.add_view(InsureView(Insure, db.session, name=u"保险管理"))
    admin.add_view(LimitView(Limit, db.session, name=u"限制管理"))
    admin.add_view(AccidentView(Accident, db.session, name=u"事故"))
    admin.add_view(MoveView(Move, db.session, name=u"调车"))
    admin.add_view(ApplyView(Apply, db.session, name=u"用车"))
    admin.add_view(IntegralView(Integral, db.session, name=u"积分"))



class UploadWidget(form.ImageUploadInput):
    def get_url(self, field):
        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = "http://" + field.url_relative_path + filename
        return filename


class ImageUpload(form.ImageUploadField):
    widget = UploadWidget()

    def _save_file(self, data, filename):
        path = self._get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        data.seek(0)
        data.save(path)
        qiniu_store = Qiniu(current_app)
        with open(path, 'rb') as fp:
            ret, info = qiniu_store.save(fp, filename)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", ret)
            # shutil.rmtree(os.path.dirname(path))
            return filename


class AdminModel(ModelView):
    column_default_sort = ('id', True)

    def is_accessible(self):
        if flask_login.current_user.is_authenticated and flask_login.current_user.role == 1:
            return True
        else:
            return False


# KPI
class KPIView(AdminIndexView):
    @expose('/')
    def index(self):
        data = Order.query.filter_by(status="ok").all()
        SumData = getOrderSumFromAdminData(data)
        return self.render('myAdmin/KPI.html', summary_data=SumData)


# super admin models
class AccidentView(AdminModel):
    can_edit = False
    column_labels = dict(Car=u"车牌", User=u"管理员", repaircompany=u"维修公司", theircarcode=u"对方车牌", isureaompany=u"保险公司",
                         isureprice=u"理赔金额", theirprice=u"对方修车费用", created_at=u'创建时间')
    column_exclude_list = ('img1', 'img2', 'img3', 'img4', 'img5', 'img6')


class MoveView(AdminModel):
    can_edit = False
    column_labels = dict(created_at=u'创建时间', User=u"管理员", Car=u'车牌', fromServerstop=u'从', toServerstop=u'到',
                         fromkm=u'发车里程', tokm=u'到达里程')


class ApplyView(AdminModel):
    can_edit = False
    column_labels = dict(created_at=u'创建时间', User=u"管理员", Car=u'车牌', comment=u'用途')


class CarView(AdminModel):
    # Override displayed fields
    # column_list = ("title", "create_at", "view_count",
    #                "category", "is_full", "status","max_book_count")
    column_exclude_list = ('img')
    form_excluded_columns = ('accidents', 'moves', 'applies', 'orders')
    column_labels = dict(created_at=u'创建时间', name=u'车牌', buy_at=u'购买时间', status=u'状态'
                         , Gps=u'设备', Cartype=u'车型', histories=u"历史", orders=u'订单', image=u"头像", mendhistories=u'维修历史')

    form_extra_fields = {
        'img': ImageUpload(u"图像", base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    column_searchable_list = ("name",)





class GpsView(AdminModel):
    column_labels = dict(cars=u"车辆", code=u'设备码')


class CustomerView(AdminModel):
    column_labels = dict(created_at=u'创建时间', name=u'姓名', gender=u'性别', idcode=u'身份证'
                         , comment=u'备注', driveage=u'驾龄', phone=u'电话', status=u'状态', histories=u"历史", orders=u'订单',
                         image=u"头像", olduser=u"老用户", integral=u"通力币",refereephone=u"推荐人电话")
    column_exclude_list = ('img', 'password')
    form_extra_fields = {
        'img': ImageUpload(u"头像", base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    form_excluded_columns = ('img', 'password', 'openid', '')
    column_searchable_list = ("name", "phone")
    column_editable_list = ("olduser",)

    def get_query(self):
        return super(CustomerView, self).get_query().filter(self.model.name != None)

    def get_count_query(self):
        return super(CustomerView, self).get_count_query().filter(self.model.name != None)


class UserView(AdminModel):
    form_extra_fields = {
        'password': PasswordField(u'密码')
    }
    column_labels = dict(name=u'用户名', password=u'密码', Userrole=u'角色', upid=u"上级", phone=u"电话")
    column_list = ("id", "name", 'Userrole', 'upid', 'phone')
    form_columns = ("name", "password", 'Userrole', 'openid', 'upid', 'phone')
    column_editable_list = ("name", "Userrole", "upid", 'openid', 'phone')

    def on_model_change(self, form, model, is_created):
        password = model.password
        md5 = hashlib.md5()
        md5.update(password)
        model.password = md5.hexdigest()


class PreferentialView(AdminModel):
    column_labels = dict(name=u'优惠名', password=u'密码', status=u'状态', mincount=u"最小购买数", minfee=u"最低消费额",
                         cutfee=u"固定折扣金额", discount=u"折扣率", multicount=u"是否乘数量", maxcutfee=u"最大折扣金额", cartypes=u'车型',
                         orders=u"订单",
                         created_at=u"创建时间", justnew=u"只针对新用户", prior=u"优先级", weekday=u"只限工作日", weekend=u"只限周末",
                         start_at=u"开始时间", end_at=u"结束时间")
    form_extra_fields = {
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    form_excluded_columns = ('orders', 'created_at', 'Cartype')


class CartypeView(AdminModel):
    column_exclude_list = ('img')
    form_excluded_columns = ('orders', "Insure", "Preferential")
    column_labels = dict(preferentials=u"所用优惠", created_at=u'创建时间', name=u'车名', price=u'价格/分', status=u'状态',
                         cars=u'该类车辆', Carcat=u"种类", count=u"剩余数量", Limit=u'限制类型', insures=u"保险")
    # column_formatters = dict(price=lambda v, c, m, p: None if not m.price else int(m.price) / 100)
    form_extra_fields = {
        'img': ImageUpload('Image', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    column_editable_list = ("Limit", "preferentials")
    column_formatters = dict(count=lambda v, c, m, p: m.remind_count)


class InsureView(AdminModel):
    column_labels = dict(name=u"名称", detail=u'详情', price=u'价格/分', cartypes=u"车型")
    form_excluded_columns = ('orders', 'Cartype')
    # column_formatters = dict(price=lambda v, c, m, p: None if not m.price else int(m.price) / 100)


class LimitView(AdminModel):
    column_labels = dict(name=u"描述", start_at=u'起始时间', end_at=u'终止时间', mincount=u'起租天数', maxcount=u'最大天数')

    # column_formatters = dict(price=lambda v, c, m, p: None if not m.price else int(m.price) / 100)


class CarcatView(AdminModel):
    column_labels = dict(name=u"名称", cars=u'该类车型', Carcat=u"种类")


class ServerstopView(AdminModel):
    column_labels = dict(name=u"名称", owner=u'管理员', phone=u"电话", lat=u"纬度", lng=u"经度", User=u'代理', Location=u"区域")
    form_excluded_columns = ('orders', "moves", "mfroms", "mtos")
    column_editable_list = ("User", "Location")


class LocationView(AdminModel):
    column_labels = dict(name=u"名称")

class IntegralView(AdminModel):
    column_labels = dict(name=u"名称",ration=u"值")
    column_editable_list = ("ration",)

def formatPayAt(patAt):
    if patAt:
        return u"%s年%s月%s日，%s：%s：%s" % (
            patAt[:4], patAt[4:6], patAt[6:8], patAt[8:10], patAt[10:12], patAt[12:14])

    else:
        return ""

def getMasterData(id,index):
    km=None
    carname=None
    order = Order.query.filter_by(id=id).first()
    if not order:
        return None
    if order.ordertype != "continue":
        if order.Car:
            carname = order.Car.name

        if order.kmbefore and order.kmafter:
            try:
                km = float(order.kmafter) - float(order.kmbefore)
            except:
                pass

        MasterData = [order.fromdate, order.todate, order.kmbefore, order.kmafter,km,carname]
        return MasterData[index]
    if not order.sourceid:
        return None
    masterOrder = GetMasterOrder(order.sourceid)
    if not masterOrder:
        return None
    if masterOrder.kmbefore and  masterOrder.kmafter:
        try:
            km = float(masterOrder.kmafter) - float(masterOrder.kmbefore)
        except:
            pass
    if masterOrder.Car:
        carname = masterOrder.Car.name
    MasterData = [masterOrder.fromdate,masterOrder.todate,masterOrder.kmbefore,masterOrder.kmafter,km,carname]

    return MasterData[index]




class OrderView(AdminModel):
    can_export = True
    export_types = ['xlsx']
    list_template = 'myAdmin/order.html'

    @expose('/overdate')
    def overdate(self):
        # Get URL for the test view method
        ds = "flt1_56=1"
        if "?" in request.url:
            args = request.url.split("?")[-1] if "?" in request.url else ""
            return redirect(url_for("order.index_view") + "?" + args + "&" + ds)
        return redirect(url_for("order.index_view") + "?" + ds)

    @expose('/yesterday')
    def yesterday(self):
        # Get URL for the test view method
        s, e = getLastYesterdayRange()
        ds = "flt2_4=" + dateStringMakerForFilter(s) + "+to+" + dateStringMakerForFilter(e)
        if "?" in request.url:
            args = request.url.split("?")[-1] if "?" in request.url else ""
            return redirect(url_for("order.index_view") + "?" + args + "&" + ds)
        return redirect(url_for("order.index_view") + "?" + ds)

    @expose('/lastweek')
    def lastweek(self):
        # Get URL for the test view method
        s, e = getLastWeekRange()
        ds = "flt2_4=" + dateStringMakerForFilter(s) + "+to+" + dateStringMakerForFilter(e)
        if "?" in request.url:
            args = request.url.split("?")[-1] if "?" in request.url else ""
            return redirect(url_for("order.index_view") + "?" + args + "&" + ds)
        return redirect(url_for("order.index_view") + "?" + ds)

    @expose('/lastmonth')
    def lastmonth(self):
        # Get URL for the test view method
        s, e = getLastMonthRange()
        ds = "flt2_4=" + dateStringMakerForFilter(s) + "+to+" + dateStringMakerForFilter(e)
        if "?" in request.url:
            args = request.url.split("?")[-1] if "?" in request.url else ""
            return redirect(url_for("order.index_view") + "?" + args + "&" + ds)
        return redirect(url_for("order.index_view") + "?" + ds)

    def get_query(self):
        return super(OrderView, self).get_query().filter(self.model.status == "ok")

    def get_count_query(self):
        return super(OrderView, self).get_count_query().filter(self.model.status == "ok")

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        joins = {}
        count_joins = {}

        query = self.get_query()
        count_query = self.get_count_query() if not self.simple_list_pager else None

        # Ignore eager-loaded relations (prevent unnecessary joins)
        # TODO: Separate join detection for query and count query?
        if hasattr(query, '_join_entities'):
            for entity in query._join_entities:
                for table in entity.tables:
                    joins[table] = None

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(query,
                                                                        count_query,
                                                                        joins,
                                                                        count_joins,
                                                                        search)

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(query,
                                                                         count_query,
                                                                         joins,
                                                                         count_joins,
                                                                         filters)

        # Calculate number of rows if necessary
        count = count_query.scalar() if count_query else None
        from sqlalchemy.orm import joinedload
        # Auto join
        for j in self._auto_joins:
            query = query.options(joinedload(j))

        # Sorting
        query, joins = self._apply_sorting(query, joins, sort_column, sort_desc)
        self.current_all_query = query
        self.current_filter = filters
        # Pagination
        query = self._apply_pagination(query, page, page_size)

        # Execute if needed
        if execute:
            query = query.all()

        return count, query

    def get_sum(self):
        if self.current_all_query:
            allData = self.current_all_query.all()
            return getOrderSumFromAdminData(allData)
        else:
            return None

    def render(self, template, **kwargs):
        if template == 'myAdmin/order.html':
            # append a summary_data dictionary into kwargs
            kwargs['summary_data'] = self.get_sum()
            if len(self.current_filter) >= 1:
                filterRawList = self.current_filter[0][2].split(" ")
                if len(filterRawList) == 5:
                    kwargs['current_filter_name'] = self.current_filter[0][1]
                    kwargs['current_filter'] = filterRawList[0] + " - " + filterRawList[3]

        return super(OrderView, self).render(template, **kwargs)

    @property
    def can_refund(self):
        self.id = request.args.get('id')
        if self.id:
            if self.get_one(request.args.get('id')).status == "refunding":
                return True
            else:
                return False
        else:
            return False

    column_searchable_list = ("Customer.name",)

    column_labels = dict(created_at=u'创建时间', tradetype=u'交易类型', Cartype=u'车辆型号', cartype=u"车型", car=u"车牌"
                         , totalfee=u'总价', Customer=u'客户', customer=u'客户', status=u'订单状态', pay_at=u'付款时间',
                         fromdate=u'起租时间',
                         todate=u'交还时间',
                         offlinefee=u'金额/分', cutfee=u"折扣价格",
                         oldfee=u"原始价格", Preferential=u"活动名", proofimg=u"存证图片", carbeforeimg=u"交车图片",
                         carendimg=u"还车图片", Car=u"分配车辆", location=u"位置", Serverstop=u"服务站", serverstop=u"服务站",
                         count=u"天数",
                         Insure=u"保险", insurefee=u"保险价格", carfee=u"车费", tradeno=u"订单号", book_at=u"预约时间", name=u"名",
                         integralfee=u"积分抵扣", ordertype=u"订单类型", kmbefore=u"发车公里", kmafter=u"收车里程",
                         km=u"行驶里程", Owner=u"代理", isoverdate=u"超期状态", pretodate=u"预计回车", serverstoplocation=u"地区",perprice=u"单价")

    edit_template = 'admin/order.html'
    column_list = (
        "id", "ordertype", 'isoverdate', "created_at", "Serverstop", "serverstoplocation", "Owner", "Car", "Cartype", "Preferential",
        "perprice", "count", "totalfee", "integralfee","Customer","pay_at", "fromdate","todate", "pretodate", "kmbefore", "kmafter", "km",
        "book_at")
    form_columns = (
        "fromdate", "todate", "Customer", "Cartype", "Car", 'proofimg',
        'carbeforeimg', 'carendimg')
    column_filters = (
        "created_at", "fromdate", "todate", "Customer.name", "Cartype.name", "Car.name", "Serverstop.name", "ordertype",
        'isoverdate', "pretodate", "serverstoplocation")


    column_formatters = dict(pay_at=lambda v, c, m, p: formatPayAt(m.pay_at),
                             offlinefee=lambda v, c, m, p: None if not m.offlinefee else float(m.offlinefee) / 100,
                             oldfee=lambda v, c, m, p: None if not m.oldfee else float(m.oldfee) / 100,
                             cutfee=lambda v, c, m, p: None if not m.cutfee else float(m.cutfee) / 100,
                             insurefee=lambda v, c, m, p: None if not m.insurefee else float(m.insurefee) / 100,
                             totalfee=lambda v, c, m, p: None if not m.totalfee else float(m.totalfee) / 100,
                             ordertype=lambda v, c, m, p: u"正常" if m.ordertype == "normal" else u"续租",
                             # preToDate=lambda v, c, m, p: getPreToDate(m),
                             fromdate = lambda v, c, m, p: m.fromdate if m.fromdate   else getMasterData(m.id,0),
                             todate=lambda v, c, m, p: m.todate if  m.todate  else getMasterData(m.id,1),
                             kmbefore=lambda v, c, m, p: m.kmbefore if  m.kmbefore else getMasterData(m.id,2),
                             kmafter=lambda v, c, m, p: m.kmafter if m.kmafter  else getMasterData(m.id,3),

                             km=lambda v, c, m, p: getMasterData(m.id,4)  if getMasterData(m.id,4)   else None,
                             Car=lambda v, c, m, p: m.Car if  m.Car  else getMasterData(m.id,5),
                             Owner=lambda v, c, m, p: m.Serverstop.User.name if m.Serverstop.User.name else u"服务站未分配代理",
                             Preferential=lambda v, c, m, p: json.loads(m.preferentialdetail)["name"] if m.preferentialdetail and  json.loads(
                                 m.preferentialdetail) and json.loads(m.preferentialdetail).has_key('name') else u"-",

                             isoverdate=lambda v, c, m, p: u"超期" if m.isoverdate == 1 else u"正常",
                             )

    # column_editable_list = ("fromdate", "todate", "Car")

    @property
    def form_extra_fields(self):
        rawStatuses = current_app.config.get("ORDER_STATUS")
        Statuses = []
        for i in rawStatuses:
            Statuses.append((i, rawStatuses[i][0]))
        return {
            'status': SelectField(u'status', choices=Statuses),
            'proofimg': ImageUpload(u'存证图片', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                                    url_relative_path=getQiniuDomain()),
            'carbeforeimg': ImageUpload(u'交车图片', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                                        url_relative_path=getQiniuDomain()),
            'carendimg': ImageUpload(u'还车图片', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                                     url_relative_path=getQiniuDomain())
        }


def on_model_change(self, form, model, is_created):
    if is_created:
        current_user = flask_login.current_user
        model.userid = current_user.id
        model.tradetype = u"offline"
        model.status = "ok"


# 管理员model
class Admin1Model(ModelView):
    def is_accessible(self):
        if flask_login.current_user.is_authenticated and flask_login.current_user.role == 2:
            return True
        else:
            return False


class UserView1(Admin1Model, UserView):
    def get_query(self):
        current_user = flask_login.current_user
        return self.session.query(self.model).filter(self.model.id == current_user.id)


class OrderView1(Admin1Model, OrderView):
    def get_query(self):
        current_user = flask_login.current_user
        return self.session.query(self.model).filter(self.model.userid == current_user.id)

    def get_count_query(self):
        current_user = flask_login.current_user
        return self.session.query(func.count('*')).filter(self.model.userid == current_user.id)

    can_edit = False
    can_delete = False
