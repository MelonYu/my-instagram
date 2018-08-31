#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   views.py
 
@Time    :   18-8-28 上午11:43
"""

from instagram import app, db
from instagram.models import Image, User, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import random
import hashlib
import json
import uuid
import os
from flask_login import login_user, logout_user, current_user, login_required
from qiniusdk import qiniu_upload_file


@app.route('/')
def index():
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=3, error_out=False)
    # print(images)
    return render_template("index.html", images=paginate.items, has_next=paginate.has_next)


@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    img_lists = {'has_next': paginate.has_next}
    images = []
    for img in paginate.items:
        comments = []
        for i in range(0, min(2, len(img.comments))):
            comment = img.comments[i]
            comments.append({'username': comment.user.username,
                             'user_id': comment.user_id,
                             'content': comment.content})
        imgvo = {'id': img.id,
                 'url': img.url,
                 'comment_count': len(img.comments),
                 'user_id': img.user_id,
                 'user_name': img.user.username,
                 'head_url': img.user.head_url,
                 'created_date': str(img.create_date),
                 'comments': comments}
        images.append(imgvo)

    img_lists['images'] = images
    return json.dumps(img_lists)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)

    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/reglogin/')
def reglogin():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))


def redirect_with_msg(target, msg, category):
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/reglogin/', "用户名或密码不能为空", 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect_with_msg('/reglogin/', "用户名不存在", 'reglogin')

    m = hashlib.md5()
    m.update((password+user.salt).encode('utf-8'))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/reglogin/', "密码错误", 'reglogin')

    login_user(user)

    next = request.values.get('next')
    if next is not None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/reg/', methods={'get', 'post'})
def reg():
    # request.args request.form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    user = User.query.filter_by(username=username).first()

    if username == '' or password == '':
        return redirect_with_msg('/reglogin/', "用户名或密码不能为空", 'reglogin')

    if user is not None:
        return redirect_with_msg('/reglogin/', "用户名已经存在",'reglogin')

    # 更多判断

    salt = '.'.join(random.sample('0123456789abcdABCD', 5))
    m = hashlib.md5()
    m.update((password+salt).encode('utf-8'))
    password = m.hexdigest()

    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


def save_to_qiniu(file, file_name):
    return qiniu_upload_file(file, file_name)


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/upload/', methods={"post"})
@login_required
def upload():
    file = request.files['file']
    # http://werkzeug.pocoo.org/docs/0.10/datastructures/
    # 需要对文件进行裁剪等操作
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        url = qiniu_upload_file(file, file_name)
        # url = save_to_local(file, file_name)
        if url is not None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code": 0, "id": comment.id,
                       "content": comment.content,
                       "username": comment.user.username,
                       "user_id": comment.user_id})
