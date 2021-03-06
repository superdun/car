# -*- coding:utf-8 -*-
import hashlib
from flask import  render_template, request, redirect, url_for,Blueprint
import flask_login
from app import login_manager
from ..models.dbORM import Customer
login_bp = Blueprint('login',__name__)




@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template("login.html")


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    password = request.form.get('password')
    if password == "":
        return
    if username not in users:
        return

    user = User()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!

    user.is_authenticated = request.form[
                                'password'] == users[username]['password']

    return user


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('admin')
        return render_template('login.html')

    username = request.form['username']
    if username not in users:
        return 'wrong username'
    md5 = hashlib.md5()
    if request.form['password'] == "":
        return render_template('wechat/login.html')
    md5.update(request.form['password'])
    psswd = md5.hexdigest()
    if psswd == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('login.protected'))

    return render_template('wechat/login.html')


@login_bp.route('/protected')
@flask_login.login_required
def protected():
    return redirect('/wx/index')


@login_bp.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/wx/index')
