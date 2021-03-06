#!/usr/bin/env python

# -*- encoding= utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   manage.py
 
@Time    :   18-8-28 上午11:39
"""

from instagram import app, db
from flask_script import Manager
from instagram.models import User, Image, Comment
import random

manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0,1000)) +'m.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 20):
        db.session.add(User('User' + str(i), 'a' + str(i)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0, 5):
                db.session.add(Comment('This is a comment ' + str(k), 1+3*i+j, i+1))
    db.session.commit()


if __name__ == '__main__':
    manager.run()
