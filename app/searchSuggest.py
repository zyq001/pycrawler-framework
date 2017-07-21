##!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import multiprocessing
import random
from xml.etree import ElementTree

# def print_node(node):
#     '''''打印结点基本信息'''
#     print "=============================================="
#     print "node.attrib:%s" % node.attrib
#     if node.attrib.has_key("age") > 0 :
#         print "node.attrib['age']:%s" % node.attrib['age']
#     print "node.tag:%s" % node.tag
#     print "node.text:%s" % node.text
import MySQLdb
import time

import re

import requests
import yaml
import hashlib

from Config import EADHOST, EADPASSWD
from dao.connFactory import getDushuConnCsor

ua = 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'
capListAPIDeviceInfo = '&soft_id=1&ver=110817&platform=an&placeid=1007&imei=862953036746111&cellid=13&lac=-1&sdk=18&wh=720x1280&imsi=460011992901111&msv=3&enc=666501479540451111&sn=1479540459901111&vc=e8f2&mod=M3'


def indexBookSuggest(st = 200000):
    conn2, csor2 = getDushuConnCsor()

    csor2.execute("select id,title,author from cn_dushu_book where id >= %s", (st,))
    conn2.commit()
    results = csor2.fetchall()
    baseUrl = 'http://123.56.66.33:19200/dushu/suggest/'
    for book in results:
        id = book[0]
        title = book[1]
        author = book[2]
        # tags = book[3]

        bookObj = dict()
        sinput = []
        sinput.append(title)
        sinput.append(author)
        # if tags:
        #     ts = json.loads(tags)
        #     for t in ts:
        #         sinput.append(t)
        inputBoj = dict()
        inputBoj['input'] = sinput
        inputBoj['output'] = title + "(" + author + ')'
        bookObj['testsuggest'] = inputBoj
        try:
            r = requests.put(baseUrl + str(id), data = json.dumps(bookObj))
            print r.text
        except Exception as e:
            print bookObj, e

if __name__ == '__main__':
    # updateCapDigest()
    indexBookSuggest()
    # handleWebsiteNoise(581398, 582410)
    import sys
    # uploadCapByCid(int(sys.argv[1]))
    # uploadCapFromTo(699818, 700000)
    # uploadCapFromTo(int(sys.argv[1]), int(sys.argv[2]))

    # shuqCategory2 = loadShuQC()

    # start(3980892,shuqCategory2)
    # start(115468,shuqCategory2)
    # shuqiAddInit()
    # from multiprocessing import Pool
    #
    # manager = multiprocessing.Manager()
    #
    # # 父进程创建Queue，并传给各个子进程：
    # queue = manager.Queue(maxsize=100)
    #
    # p = Pool(3)
    #
    # p.apply_async(onlyInsertCap, args=(queue,))
    # # p.apply_async(onlyInsertCap, args=(queue,))
    # # p.apply_async(onlyInsertCap, args=(queue,))
    # #
    # startFromCId(p,queue)
    # ids = '6692553,4871569,5067938,57392,51602'
    # for bookId in ids.split(','):
    #     start(bookId, shuqCategory2)
    # startFromLatestAjax()
