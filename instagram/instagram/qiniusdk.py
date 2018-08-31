#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :   Amelia 
@Contact :   yu_mengling@hust.edu.cn
@File    :   qiniusdk.py
 
@Time    :   18-8-31 下午12:02
"""

import os
from instagram import app
from qiniu import Auth, put_stream, put_file, put_data


# 需要填写你的 Access Key 和 Secret Key
access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']

# 构建鉴权对象
q = Auth(access_key, secret_key)
# 要上传的空间
bucket_name = app.config['QINIU_BUCKET_NAME']
domain_prefix = app.config['QINIU_DOMAIN']

save_dir = app.config['UPLOAD_DIR']


def qiniu_upload_file(source_file, save_file_name):
    # 生成上传Token, 可以指定过期时间等
    token = q.upload_token(bucket_name, save_file_name)

    # ret, info = put_file(token, save_file_name, os.path.join('/home/amelia/Pictures/upload/', source_file))
    ret, info = put_data(token, save_file_name, source_file.stream.read())

    if info.status_code == 200:
        return domain_prefix + save_file_name

    return None

