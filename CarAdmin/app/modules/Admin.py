# -*- coding: utf-8 -*-
from flask import request
import os
import os.path as op
import time
from flask_admin import Admin
import flask_login
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import func
from jinja2 import Markup
from flask import current_app
from ..models.dbORM import *
from ..helpers import thumb
from flask_qiniustorage import Qiniu
from wtforms import SelectField, PasswordField
from flask_admin import BaseView, expose
import hashlib
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
    admin = Admin(current_app, name=u'通力后台管理')
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
    # admin.add_view(OrderAdminView(name=u'订单管理', endpoint='refund'))
    admin.add_view(InsureView(Insure, db.session, name=u"保险管理"))


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


# super admin models
class CarView(AdminModel):
    # Override displayed fields
    # column_list = ("title", "create_at", "view_count",
    #                "category", "is_full", "status","max_book_count")
    column_exclude_list = ('img')
    column_labels = dict(created_at=u'创建时间', name=u'车牌', buy_at=u'购买时间', status=u'状态'
                         , Gps=u'设备', Cartype=u'车型', histories=u"历史", orders=u'订单', image=u"头像", mendhistories=u'维修历史')

    form_extra_fields = {
        'img': ImageUpload(u"图像", base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }


class GpsView(AdminModel):
    column_labels = dict(cars=u"车辆", code=u'设备码')


class CustomerView(AdminModel):
    column_labels = dict(created_at=u'创建时间', name=u'姓名', gender=u'性别', idcode=u'身份证'
                         , comment=u'备注', driveage=u'驾龄', phone=u'电话', status=u'状态', histories=u"历史", orders=u'订单',
                         image=u"头像")
    column_exclude_list = ('img', 'password', '')
    form_extra_fields = {
        'img': ImageUpload(u"头像", base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    form_excluded_columns = ('img', 'password', 'openid', '')


class UserView(AdminModel):
    form_extra_fields = {
        'password': PasswordField(u'密码')
    }
    column_labels = dict(name=u'用户名', password=u'密码', Userrole=u'角色')
    column_list = ("name", 'Userrole')
    form_columns = ("name", "password", 'Userrole', 'openid')

    def on_model_change(self, form, model, is_created):
        password = model.password
        md5 = hashlib.md5()
        md5.update(password)
        model.password = md5.hexdigest()


class PreferentialView(AdminModel):
    column_labels = dict(name=u'优惠名', password=u'密码', status=u'状态', mincount=u"最小购买数", minfee=u"最低消费额",
                         cutfee=u"固定折扣金额", discount=u"折扣率", multicount=u"是否乘数量", maxcutfee=u"最大折扣金额", cartypes=u'车型',
                         orders=u"订单",
                         created_at=u"创建时间")
    form_extra_fields = {
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }
    form_excluded_columns = ('orders', 'created_at')


class CartypeView(AdminModel):
    column_exclude_list = ('img')
    form_excluded_columns = ('orders')
    column_labels = dict(Preferential=u"所用优惠", created_at=u'创建时间', name=u'车名', price=u'价格/分', status=u'状态',
                         cars=u'该类车辆', Carcat=u"种类")
    # column_formatters = dict(price=lambda v, c, m, p: None if not m.price else int(m.price) / 100)
    form_extra_fields = {
        'img': ImageUpload('Image', base_path=getUploadUrl(), relative_path=thumb.relativePath(),
                           url_relative_path=getQiniuDomain()),
        'status': SelectField(u'状态', choices=(("deleted", u"已删除"), ("pending", u"暂停"), ("normal", u"正常"))),
    }


class InsureView(AdminModel):
    column_labels = dict(name=u"名称", detail=u'详情', price=u'价格/分')
    form_excluded_columns = ('orders')
    # column_formatters = dict(price=lambda v, c, m, p: None if not m.price else int(m.price) / 100)


class CarcatView(AdminModel):
    column_labels = dict(name=u"名称", cars=u'该类车型', Carcat=u"种类")


class ServerstopView(AdminModel):
    column_labels = dict(name=u"名称", owner=u'管理员', phone=u"电话", lat=u"纬度", lng=u"经度")
    form_excluded_columns = ('orders')


def formatPayAt(patAt):
    if patAt:
        return u"%s年%s月%s日，%s：%s：%s" % (
            patAt[:4], patAt[4:6], patAt[6:8], patAt[4:6], patAt[8:10], patAt[10:12])

    else:
        return ""


class OrderView(AdminModel):
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

    column_labels = dict(created_at=u'创建时间', tradetype=u'交易类型', Cartype=u'车辆型号'
                         , totalfee=u'总价', Customer=u'客户', status=u'订单状态', pay_at=u'付款时间', fromdate=u'起租时间',
                         todate=u'交还时间',
                         isrefund=u'是否退款', r_pay_at=u'退款时间', r_totalfee=u'退款金额', offlinefee=u'金额/分', cutfee=u"折扣价格",
                         oldfee=u"原始价格", Preferential=u"所用优惠", proofimg=u"存证图片", carbeforeimg=u"交车图片",
                         carendimg=u"还车图片", Car=u"分配车辆", location=u"订车位置", Serverstop=u"所选服务站", count=u"天数",
                         Insure=u"保险", insurefee=u"保险价格", carfee=u"车费")

    edit_template = 'admin/order.html'
    column_list = (
        "id", "created_at", "tradetype", "Cartype", "count", "oldfee", "cutfee", "insurefee", "totalfee", "Customer",
        "status", "pay_at", "fromdate",
        "todate",
        "isrefund", "r_pay_at", "r_totalfee", "Car", "Serverstop", "location", "Insure")
    form_columns = (
        "offlinefee", "fromdate", "todate", "Customer", "Cartype", "Car", "Serverstop", "location", 'proofimg',
        'carbeforeimg', 'carendimg')
    column_formatters = dict(pay_at=lambda v, c, m, p: formatPayAt(m.pay_at),
                             offlinefee=lambda v, c, m, p: None if not m.offlinefee else int(m.offlinefee) / 100,
                             oldfee=lambda v, c, m, p: None if not m.oldfee else int(m.oldfee) / 100,
                             cutfee=lambda v, c, m, p: None if not m.cutfee else int(m.cutfee) / 100,
                             insurefee=lambda v, c, m, p: None if not m.insurefee else int(m.insurefee) / 100,
                             totalfee=lambda v, c, m, p: None if not m.totalfee else int(m.totalfee) / 100)

    column_editable_list = ("fromdate", "todate", "Car")

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
