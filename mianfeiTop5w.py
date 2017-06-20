#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''
import json
import time

import requests

from client.shuqiUpdate import updateFromMysql
from util.timeHelper import getToday


if __name__ == '__main__':
    top = open('local/top5w.txt')

    searchInput = {
        "name": "",
        "andCrawl":True,
        "top":2
    }

    while 1:
        name = top.readline()
        if not name:
            break
        searchInput['name'] = name.replace('\n', '')
        r = requests.post('http://0.0.0.0:10008/search', data = json.dumps(searchInput))
        print r.text