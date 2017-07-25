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

def upload2Bucket(id, obj):

    try:
        bucket.put_object(id, obj)
        # print 'succ upload ',id
    except Exception as e:
        print id, ' upload faild ',e


