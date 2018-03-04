# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, jsonify, request, Response, redirect
from flask_admin import Admin, BaseView, expose
from flask_admin.helpers import get_url

from flask_admin._compat import string_types, urljoin
from flask_admin.contrib.sqla import ModelView
from wtforms import Form as wtForm
from dbORM import db, User,Gzh
from wtforms import TextAreaField, SelectField
from wtforms.widgets import TextArea
import thumb
from flask_qiniustorage import Qiniu
from jinja2 import Markup
from flask_admin import form
from flask_admin.form import rules
import flask_login
import os
import os.path as op
from moduleGlobal import app, admin,qiniu_store, QINIU_DOMAIN, CATEGORY, UPLOAD_URL
import time

def date_format(value):
    return time.strftime(u'%Y/%m/%d %H:%M:%S', time.localtime(float(value)))
def img_url_format(value):
    return Markup("<img src='%s'>" %("http://"+QINIU_DOMAIN+value))

def dashboard():


    admin.add_view(UserView(User, db.session))
    admin.add_view(GzhView(Gzh, db.session))

class UploadWidget(form.ImageUploadInput):
    def get_url(self, field):
        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = "http://"+field.url_relative_path+filename
        return filename


class ImageUpload(form.ImageUploadField):
    widget = UploadWidget()
    def _save_file(self, data, filename):
        path = self._get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        data.seek(0)
        data.save(path)
        with open(path, 'rb') as fp:
            ret, info = qiniu_store.save(fp, filename)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", ret)
            #shutil.rmtree(os.path.dirname(path))
            return filename


class GzhView(ModelView):
    def is_accessible(self):

        return flask_login.current_user.is_authenticated

    # Override displayed fields
    # column_list = ("title", "create_at", "view_count",
    #                "category", "is_full", "status","max_book_count")


    form_extra_fields = {
        'img': ImageUpload('Image', base_path=UPLOAD_URL, relative_path=thumb.relativePath(),url_relative_path=QINIU_DOMAIN),
        # 'category': SelectField(u'category', choices=CATEGORY),
        'status': SelectField(u'status', choices=[('published', u'发布'), ('deleted', u'删除')]),
        # 'is_full': SelectField(u'is_full', choices=[("no", u'未满'),("yes", u'已满'),("almost",u"快满了")])
    }
    column_formatters = dict(created_at=lambda v, c, m, p: date_format(m.created_at),
                             img=lambda v, c, m, p: img_url_format(m.img))
    form_columns = ("name", "url","img")
    form_excluded_columns = ('create_at')
    # create_template = 'admin/post/create.html'
    # edit_template = 'admin/post/edit.html'



class UserView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
    column_list = ("name", "auth")
    form_columns = ("name", "auth")
