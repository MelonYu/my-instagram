#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   views.py
 
@Time    :   18-8-28 上午11:43
"""

from instagram import app, db
from instagram.models import Image, User
from flask import render_template


@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    print(images)
    return render_template("index.html", images=images)

@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    return render_template('profile.html',user_id=user_id)