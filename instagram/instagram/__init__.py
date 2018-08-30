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
# from flask_login import LoginManager
import flask_login

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')
app.secret_key = 'amelia'
db = SQLAlchemy(app)
login_manager = flask_login.LoginManager(app)
login_manager.login_view = '/reglogin/'

from instagram import views, models
