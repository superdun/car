# -*- coding: utf-8 -*-
from flask import request
import os
import os.path as op
import time
from flask_admin import Admin
import flask_login
from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup
from flask import current_app
from db.dbORM import db, User, Car, Gps, Customer, Cartype, Order
from helpers import thumb
from flask_qiniustorage import Qiniu
from wtforms import SelectField, StringField
from flask_admin import BaseView, expose
admin = Admin(current_app)
QINIU_DOMAIN = current_app.config.get('QINIU_BUCKET_DOMAIN', '')
UPLOAD_URL = current_app.config.get('UPLOAD_URL')


def date_format(value):
    return time.strftime(u'%Y/%m/%d %H:%M:%S', time.localtime(float(value)))


def img_url_format(value):
    return Markup("<img src='%s'>" % ("http://" + QINIU_DOMAIN + value))


def dashboard():
    admin.add_view(UserView(User, db.session))
    admin.add_view(CarView(Car, db.session))
    admin.add_view(GpsView(Gps, db.session))
    admin.add_view(CustomerView(Customer, db.session))
    admin.add_view(CartypeView(Cartype, db.session))
    admin.add_view(OrderView(Order, db.session))
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


class CarView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    # Override displayed fields
    # column_list = ("title", "create_at", "view_count",
    #                "category", "is_full", "status","max_book_count")

    form_extra_fields = {
        'img': ImageUpload('Image', base_path=UPLOAD_URL, relative_path=thumb.relativePath(),
                           url_relative_path=QINIU_DOMAIN),
        'status': SelectField(u'status', choices=("deleted", "pending", "normal")),
    }
    # column_formatters = dict(created_at=lambda v, c, m, p: date_format(m.created_at),
    #                          img=lambda v, c, m, p: img_url_format(m.img))
    # form_columns = ("name", "url","img")
    # form_excluded_columns = ('create_at')
    # create_template = 'admin/post/create.html'
    # edit_template = 'admin/post/edit.html'


class GpsView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated


class CustomerView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    form_extra_fields = {
        'img': ImageUpload('Image', base_path=UPLOAD_URL, relative_path=thumb.relativePath(),
                           url_relative_path=QINIU_DOMAIN),
        # 'category': SelectField(u'category', choices=CATEGORY),
    }
    form_excluded_columns = ('img', 'password')


class UserView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    column_list = ("name", "auth")
    form_columns = ("name", "auth")


class CartypeView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    column_formatters = dict(price=lambda v, c, m, p: float(m.price) / 100)


def formatPayAt(patAt):
    if patAt:
        return u"%s年%s月%s日，%s：%s：%s" % (
            patAt[:4], patAt[4:6], patAt[6:8], patAt[4:6], patAt[8:10], patAt[10:12])

    else:
        return ""
class OrderView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
    @property
    def can_refund(self):
        self.id = request.args.get('id')
        if self.get_one(request.args.get('id')).status=="refunding":
            return True
        else:
            return False
    edit_template = 'admin/order.html'
    column_exclude_list = ("detail", "tradetype", "prepayid", "refundorder","wxtradeno")
    form_excluded_columns = ("detail", "tradetype", "prepayid", "refundorder")
    column_formatters = dict(pay_at=lambda v, c, m, p:formatPayAt(m.pay_at))

    # form_ajax_refs = {
    #     'Cartype': {
    #         'fields': ['name', 'price'],
    #         'page_size': 10
    #     }
    # }
# class OrderAdminView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/order.html')