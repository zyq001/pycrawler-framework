#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
dao实现类，实现对entity的增删改查
 zyq

'''
import json
import random
import re

import time

import MySQLdb

from dao.aliyunOss import upload2Bucket
from dao.connFactory import getDushuConnCsor
from parse.easouParser import getAndParse
from util.UUIDUtils import getBookDigest
from util.pyBloomHelper import getBloom, dumpBloomToFile

db_dushu = 'cn_dushu_book'
db_acticle = 'cn_dushu_acticle'


def getZssqAllLianZaiBookObjs():
    '''
    获取所有免费TXT的主键和相关信息：id,rawUrl,chapterNum,source,digest
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    dictCsor.execute("SELECT id,rawUrl,chapterNum,source,digest from cn_dushu_book where  "
                 "bookType = '连载' and rawUrl like 'http://api.zhuishushenqi.com/book/%' "
                     ";")
    conn.commit()
    bookObjs = dictCsor.fetchallDict()

    csor.close()
    conn.close()

    return bookObjs

def getShuqiAllBookObjs():
    '''
    获取所有Shuqi的主键和相关信息：id,rawUrl,chapterNum,source,digest
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    dictCsor.execute("SELECT id,rawUrl,chapterNum,source,digest from cn_dushu_book where operateStatus = 0  "
                 " and rawUrl like 'http://api.shuqireader.com/reader/bc_cover.php%';")
    conn.commit()
    bookObjs = dictCsor.fetchallDict()

    csor.close()
    conn.close()

    return bookObjs


def getShuqiIdRawUrlAsBookObjs():
    '''
    获取所有Shuqi的主键和相关信息：id,rawUrl,chapterNum,source,digest
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    dictCsor.execute("SELECT id,rawUrl from cn_dushu_book where operateStatus = 0  "
                 " and rawUrl like 'http://api.shuqireader.com/reader/bc_cover.php%';")
    conn.commit()
    bookObjs = dictCsor.fetchallDict()

    csor.close()
    conn.close()

    return bookObjs

def getCapObjsById(bookId):
    conn,csor = getDushuConnCsor()

    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    dictCsor.execute("SELECT id,title,idx from " + db_acticle + " where bookId = %s and id < 63017738;", (bookId, ))
    conn.commit()
    capObjs = dictCsor.fetchallDict()

    csor.close()
    conn.close()

    return capObjs