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

if __name__ == '__main__':
    import requests
    import json
    r = requests.get('http://dushu-content.oss-cn-shanghai.aliyuncs.com/66312274.json')

    obj = json.loads(r.text)
    content = obj['content'].replace('<br>', '</p><p>')
    if content.startswith('</p>'):
        content = content[4:]
    if content.endswith('<p>'):
        content = content[0:-3]
    obj['content'] = content


    upload2Bucket('66312274.json', json.dumps(obj))
