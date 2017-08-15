#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
日常定时更新相关运营信息："最近更新"等
@author: zyq
'''
from dao.connFactory import getDushuConnCsor
from dao.dushuService import getLatestUpdateBooks, updateOneFieldByOneField
from dao.dushuTypeBookDao import getIdsByType, updateIdsByType


def dailyLatestUpdate():

    nanShengCategorys = (9,18, 41,50,58,69,74,82,90,93,97,111)
    nvShengCategorys = (1,18,26,33,50,64,97,111)

    nanBooks = getLatestUpdateBooks(nanShengCategorys, limit=50)

    updateIdsByBooks(nanBooks,'girlbest')

    nvBooks = getLatestUpdateBooks(nvShengCategorys, limit=50)

    updateIdsByBooks(nvBooks, 'boylastest')



    # 配置是乱的
    # boyLatestIds = getIdsByType('girlbest')
    #
    #
    # girllastestIds = getIdsByType('boylastest')
    #
    # updateOneFieldByOneField('')


def updateIdsByBooks(books, confType):
    ids = ''
    for book in books:
        ids = ids + str(book['id']) + ','
    ids = ids[:-1]
    updateIdsByType(confType, ids)

if __name__ =='__main__':
    dailyLatestUpdate()