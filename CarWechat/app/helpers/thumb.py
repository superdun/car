# -*- coding:utf-8 -*-
from flask import current_app
import os
import os.path as op
import string
import random
from werkzeug import secure_filename
from flask_qiniustorage import Qiniu
import shutil
from qiniu import Auth
from qiniu import BucketManager
def upLoadFromUrl(url,id):
    access_key = current_app.config.get('QINIU_ACCESS_KEY', '')
    secret_key = current_app.config.get('QINIU_SECRET_KEY', '')

    bucket_name = current_app.config.get('QINIU_BUCKET_NAME', '')
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    key = '%s.jpg'%str(id)
    ret, info = bucket.fetch(url, bucket_name, key)
    print(info)
    return key

def relativePath():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + '/'


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(file, basePath, domain, storeModel):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pic_dir = basePath + '/' + relativePath()
        path = pic_dir + filename
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path),  0o111)

        file.seek(0)
        file.save(path)
        qiniu_file_name = relativePath() + filename
        with open(path, 'rb') as fp:
            ret, info = storeModel.save(fp, qiniu_file_name)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", info)
                
        shutil.rmtree(pic_dir)
        # return filename
        localUrl = 'http://' + domain + '/' + qiniu_file_name
        title = filename.rsplit('.', 1)[0]
        return {"status":"ok","title": title, "isImage": 1, "fileName": filename, "localUrl": localUrl, "result": 1,"relativePath":qiniu_file_name}


def upload_file_by_pillow(file,filename, basePath, domain, storeModel):
    if file :
        filename = secure_filename(filename)
        pic_dir = basePath + '/' + relativePath()
        path = pic_dir + filename
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path))

        file.save(path,'JPEG')
        qiniu_file_name = relativePath() + filename
        with open(path, 'rb') as fp:
            ret, info = storeModel.save(fp, qiniu_file_name)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", info)

        shutil.rmtree(pic_dir)
        # return filename
        localUrl = 'http://' + domain + '/' + qiniu_file_name
        title = filename.rsplit('.', 1)[0]
        return {"title": title, "isImage": 1, "fileName": filename, "localUrl": localUrl, "result": 1}