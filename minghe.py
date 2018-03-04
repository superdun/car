from flask import Flask,render_template,url_for,redirect,request
from dbORM import db, User,Gzh
import thumb
from moduleGlobal import app, qiniu_store, QINIU_DOMAIN, CATEGORY, UPLOAD_URL
import moduleAdmin as admin
import flask_login
import hashlib
from flask_paginate import Pagination, get_page_args




@app.route('/')
def index():
    return 'Hello World!'


@app.route("/gzhindex")
def gzhIndex():
    searchKey = request.args.get("s")
    previewThumb = app.config.get('PREVIEW_THUMBNAIL')
    local_img_domain = "http://" + QINIU_DOMAIN
    page, per_page, offset = get_page_args()
    per_page = app.config.get('PER_PAGE')
    if not searchKey:

        total = len(Gzh.query.filter(Gzh.status == 'published').all())
        items = Gzh.query.filter(Gzh.status == 'published').order_by('created_at desc').offset(offset).limit(
            per_page).all()


    else:
        total = len(Gzh.query.filter(Gzh.status == 'published' and Gzh.name.like("%"+searchKey+"%")).all())
        items = Gzh.query.filter(Gzh.status == 'published' and Gzh.name.like("%"+searchKey+"%")).order_by('created_at desc').offset(offset).limit(
            per_page).all()
    pagination = Pagination(page=page, total=total, per_page=per_page)
    return render_template('gzhIndex.html', items=items, pagination=pagination,
                               tailThumb=previewThumb, local_img_domain=local_img_domain)


# admin
admin.dashboard()

# login


login_manager = flask_login.LoginManager()

login_manager.init_app(app)
users = {}
raw_users = User.query.all()
for user in raw_users:
    users[user.name] = {'password': user.password}


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


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
    if username not in users:
        return

    user = User()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form[
                                'password'] == users[username]['password']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if flask_login.current_user.is_authenticated:
            return redirect('/admin')
        return render_template('login.html')

    username = request.form['username']
    if username not in users:
        return 'wrong username'
    md5 = hashlib.md5()
    psswd = md5.update(request.form['password']).hexdigest()
    if psswd == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return redirect('/admin')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

if __name__ == '__main__':
    app.run()
