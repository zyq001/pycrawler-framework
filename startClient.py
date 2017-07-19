#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''

import time

import requests

from Config import SEARCHHOST
# from app.QuanBenMianFeiCrawler import QuanBenCrawler
# from app.QuanbenUpdater import updateByDbBookId
# from app.ZhuiShuShenQiCrawler import ZssqCrawler
# from app.fixer import crawlBySearchHistory
from app.mianfeiTXTUpdater import mianfeiUpdateByBookObj
# from app.shuqiUpdater import updateFromMysql
from app.shuqi import start
from dao.dushuMianFeiTXTService import getBookByTitle, deleteNLastChaps
from util.categoryHelper import getClassifyCodeByName
# from util.timeHelper import getToday



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
    baseUrl = 'http://%s/dushu/book/'  % SEARCHHOST
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
    start(2490339)
    # print getClassifyCodeByName('魔法')
    # print getClassifyCodeByName('魔法')['typeCode']
    # print getClassifyCodeByName('魔法')['categoryCode']
    # print getClassifyCodeByName(u'魔法')['categoryCode']
    # print getClassifyCodeByName('校园魔法')['categoryCode']
    # print getClassifyCodeByName('校园魔法')['typeCode']
    # crawlBySearchHistory()
    # updateByDbBookId(2137876)
    # ZssqCrawler('587f57b38602d1eb036492f4').crawl(allowUpdate=True)
    # QuanBenCrawler('577a74c6d48745631a23962a').crawl(allowUpdate=False)
    # deleteESDocs()
    # fixUnuploadMianfeiChaps()
    # lastTime = 0
    # while 1:
    #     nowTime = time.time()
    #     sinceLastTime = nowTime - lastTime
    #     if sinceLastTime < 24 * 3600:
    #         print getToday() + ' sleep ' + str(24* 3600 - sinceLastTime) + 's until 24h after last time.'
    #         time.sleep(24* 3600 - sinceLastTime)
    #     lastTime = time.time()
    #     updateFromMysql()