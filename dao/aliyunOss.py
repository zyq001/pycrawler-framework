#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Config import OSSINTERNALENDPOINT, OSSUSER, OSSPASSWD


def getBucket():
    import oss2

    endpoint = OSSINTERNALENDPOINT  # 假设你的Bucket处于杭州区域
    # endpoint = OSSINTERNALENDPOINT  # 假设你的Bucket处于杭州区域

    auth = oss2.Auth(OSSUSER, OSSPASSWD)
    bucket = oss2.Bucket(auth, endpoint, 'dushu-content')

    return bucket

bucket = getBucket()

def uploadJson2Bucket(id,obj):
    headers={'Content-Type': 'application/json; charset=utf-8'}
    upload2Bucket(id, obj,headers=headers)

def upload2Bucket(id, obj,headers = None):

    try:
        if not headers:
            bucket.put_object(id, obj)
        else:
            bucket.put_object(id, obj, headers=headers)

        # print 'succ upload ',id
    except Exception as e:
        print id, ' upload faild ',e


