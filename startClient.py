#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''

import time

import requests

from app.mianfeiTXTUpdater import mianfeiUpdateByBookObj
from app.shuqiUpdater import updateFromMysql
from dao.dushuMianFeiTXTService import getBookByTitle, deleteNLastChaps
from util.timeHelper import getToday



def fixUnuploadMianfeiChaps():
    m2 = open('m2.log')
    while 1:
        line = m2.readline()
        if not line:
            break
        splits = line.replace('\n', '').split(' ')
        title = splits[0]
        chaps = splits[1]
        bookObjs = getBookByTitle(title)
        for bookObj in bookObjs:
            deleteNLastChaps(bookObj['id'], int(chaps) + 1)
            bookObj['chapterNum'] = bookObj['chapterNum'] - int(chaps) -1
            mianfeiUpdateByBookObj(bookObj)


def deleteESDocs():
    baseUrl = 'http://123.56.66.33:19200/dushu/book/'
    count = 12000
    for i in range(2124594, 2100000, -1):
        url = baseUrl + str(i)
        r = requests.delete(url)
        if r.status_code == 200:
            count = count -1
            if count < 1:
                return
    return count
if __name__ == '__main__':
    deleteESDocs()
    fixUnuploadMianfeiChaps()
    lastTime = 0
    while 1:
        nowTime = time.time()
        sinceLastTime = nowTime - lastTime
        if sinceLastTime < 24 * 3600:
            print getToday() + ' sleep ' + str(24* 3600 - sinceLastTime) + 's until 24h after last time.'
            time.sleep(24* 3600 - sinceLastTime)
        lastTime = time.time()
        updateFromMysql()