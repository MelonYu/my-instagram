#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   __init__.py
 
@Time    :   18-8-28 上午11:43
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')
db = SQLAlchemy(app)

from instagram import views, models
