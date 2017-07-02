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
from exception.InputException import InputException
from parse.easouParser import getAndParse
from util.UUIDUtils import getBookDigest
from util.pyBloomHelper import getBloom, dumpBloomToFile

db_dushu = 'cn_dushu_book'
db_acticle = 'cn_dushu_acticle'


def getMianAllBookObjs():
    '''
    获取所有免费TXT的主键和相关信息：id,rawUrl,chapterNum,source,digest
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()

    csor.execute("SELECT id,rawUrl,chapterNum,source,digest from cn_dushu_book where rawUrl like"
                 " 'http://api.yingyangcan.com.cn/interface/ajax/book/getbaseinfo.ajax?%' and bookType = '连载';")
    conn.commit()
    results = csor.fetchall()

    bookObjs = []
    for book in results:
        bookId = book[0]
        rawUrl = book[1]
        chapterNum = book[2]
        mid = book[3]
        if 'mianfeiTXT' in mid:
            mid = mid.replace('mianfeiTXT', '')
        bookDigest = book[4]

        bookObj = dict()
        bookObj['id'] = bookId
        bookObj['source'] = mid
        bookObj['digest'] = bookDigest
        bookObj['rawUrl'] = rawUrl
        bookObj['rawUrl'] = rawUrl
        bookObj['chapterNum'] = chapterNum

        bookObjs.append(bookObj)

    csor.close()
    conn.close()

    return bookObjs

def getMianAllBookBaseObjs():
    '''
    获取所有免费TXT的基础：id,名称作者，等
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()

    csor.execute("SELECT id,title,author,source from cn_dushu_book where rawUrl like"
                 " 'http://api.yingyangcan.com.cn/interface/ajax/book/getbaseinfo.ajax?%' and bookType = '连载' limit 10;")
    conn.commit()
    results = csor.fetchall()

    bookObjs = []
    for book in results:
        bookId = book[0]
        # chapterNum = book[1]
        mid = book[3]
        title = book[1]
        author = book[2]
        if 'mianfeiTXT' in mid:
            mid = mid.replace('mianfeiTXT', '')
        # bookDigest = book[4]

        bookObj = dict()
        bookObj['id'] = bookId
        bookObj['source'] = mid
        # bookObj['digest'] = bookDigest
        # bookObj['rawUrl'] = rawUrl
        # bookObj['rawUrl'] = rawUrl
        # bookObj['chapterNum'] = chapterNum
        bookObj['title'] = title
        bookObj['author'] = author

        bookObjs.append(bookObj)

    csor.close()
    conn.close()

    return bookObjs

def getBookByTitle(title):
    '''
    用title获取bookObj
    :return bookObjs即： [bookObj{"id":"1",,}]: 
    '''

    conn, csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    dictCsor.execute("SELECT *  from cn_dushu_book where rawUrl like"
                     " 'http://api.yingyangcan.com.cn/interface/ajax/book/getbaseinfo.ajax?%' and title = '" + title + "';")
    conn.commit()
    results = dictCsor.fetchallDict()

    # if len(results) > 1:
    #     raise InputException('more than one book')

    bookObj = results

    csor.close()
    conn.close()

    return bookObj


def deleteNLastChaps(dbBookId, limit):
    '''
    删除最新的N个章节
    :return: 
    '''
    conn, csor = getDushuConnCsor()
    csor.execute('delete from ' + db_acticle  + " where bookId = %s order by id desc limit %s;", (dbBookId, limit))
    conn.commit()

    csor.close()
    conn.close()
