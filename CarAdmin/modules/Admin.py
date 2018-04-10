# -*- coding: utf-8 -*-
from flask import request
import os
import os.path as op
import time
from flask_admin import Admin
import flask_login
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import  func
from jinja2 import Markup
from flask import current_app
from db.dbORM import db, User, Car, Gps, Customer, Cartype, Order
from helpers import thumb
from flask_qiniustorage import Qiniu
from wtforms import SelectField, PasswordField
from flask_admin import BaseView, expose
import hashlib

admin = Admin(current_app)
QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')
UPLOAD_URL = current_app.config.get('UPLOAD_URL')


def date_format(value):
    return time.strftime(u'%Y/%m/%d %H:%M:%S', time.localtime(float(value)))


def img_url_format(value):
    return Markup("<img src='%s'>" % ("http://" + QINIU_DOMAIN + value))


def dashboard():
    admin.add_view(UserView(User, db.session, name=u"员工管理"))
    admin.add_view(UserView1(User, db.session, name=u"个人资料", endpoint="profile"))
    admin.add_view(CarView(Car, db.session, name=u"车辆管理"))
    admin.add_view(GpsView(Gps, db.session, name=u"设备管理"))
    admin.add_view(CustomerView(Customer, db.session, name=u"客户管理"))
    admin.add_view(CartypeView(Cartype, db.session, name=u"车型管理"))
    admin.add_view(OrderView(Order, db.session, name=u"订单管理"))
    admin.add_view(OrderView1(Order, db.session, name=u"我的订单", endpoint="myorders"))
    # admin.add_view(OrderAdminView(name=u'订单管理', endpoint='refund'))


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

    form_extra_fields = {
        'img': ImageUpload('Image', base_path=UPLOAD_URL, relative_path=thumb.relativePath(),
                           url_relative_path=QINIU_DOMAIN),
        'status': SelectField(u'status', choices=("deleted", "pending", "normal")),
    }


class GpsView(AdminModel):
    pass


class CustomerView(AdminModel):
    form_extra_fields = {
        'img': ImageUpload('Image', base_path=UPLOAD_URL, relative_path=thumb.relativePath(),
                           url_relative_path=QINIU_DOMAIN),
        # 'category': SelectField(u'category', choices=CATEGORY),
    }
    form_excluded_columns = ('img', 'password')


class UserView(AdminModel):
    form_extra_fields = {
        'password': PasswordField(u'密码')
    }
    column_labels = dict(name=u'用户名', password=u'密码', Userrole=u'角色')
    column_list = ("name", 'Userrole')
    form_columns = ("name", "password", 'Userrole')

    def on_model_change(self, form, model, is_created):
        password = model.password
        md5 = hashlib.md5()
        md5.update(password)
        model.password = md5.hexdigest()


class CartypeView(AdminModel):
    column_formatters = dict(price=lambda v, c, m, p: float(m.price) / 100)


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
                         isrefund=u'是否退款', r_pay_at=u'退款时间', r_totalfee=u'退款金额', offlinefee=u'金额/元' )

    edit_template = 'admin/order.html'
    column_list = (
        "id", "created_at", "tradetype", "Cartype", "totalfee", "Customer", "status", "pay_at", "fromdate", "todate",
        "isrefund", "r_pay_at", "r_totalfee")
    form_columns = ("offlinefee", "fromdate", "todate", "Customer", "Cartype")
    column_formatters = dict(pay_at=lambda v, c, m, p: formatPayAt(m.pay_at))
    column_editable_list=( "fromdate", "todate")
    def on_model_change(self, form, model, is_created):
        if is_created:
            current_user = flask_login.current_user
            model.userid = current_user.id
            model.tradetype = u"offline"
            model.status= "ok"


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


