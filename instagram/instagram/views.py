#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   views.py
 
@Time    :   18-8-28 上午11:43
"""

from instagram import app

@app.route('/')
def index():
    return "ok"