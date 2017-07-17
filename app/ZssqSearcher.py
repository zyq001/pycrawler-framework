#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
将搜索功能拎出来，因为涉及加载bloom过滤，会占用较大内存
@author: zyq
'''
import json
import traceback
from urllib import quote

from Config import ZSSQSEARCHBASEURL
from app.ZhuiShuShenQiCrawler import startByZid
from dao.BookDigestBloom import bookDigestBloom
from util.UUIDUtils import getBookDigest
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA


def search(searchInput):

    if isinstance(searchInput, unicode):
        searchInput = searchInput.encode('utf-8')


    url = ZSSQSEARCHBASEURL + quote(searchInput)
    searchResContent = getContentWithUA(url)
    if not searchResContent:
        return None
    searchResObj = json.loads(searchResContent)
    if not searchResObj or not searchResObj.has_key('books'):
        return
    return searchResObj


def searchAndCrawl(searchInput, limit = 5):

    searchResObj = search(searchInput)
    succcount = 0
    count = 0
    for bookObj in searchResObj['books']:
        count += 1
        if count > 5: #只要搜索结果的前N个，后面的就算了
            break

        digest = getBookDigest(bookObj)
        if bookDigestBloom.contains(digest):
            myLogging.info('has book %s, with same author %s, skip', bookObj['title'].encode('utf-8'), bookObj['author'].encode('utf-8'))
            continue
        zid = bookObj['_id']
        try:
            startByZid(zid, allowUpdate=False)
        except Exception as e:
            myLogging.error('zid %s has exception: %s', zid, traceback.format_exc())
        succcount += 1
        if succcount > limit: #最多抓取图书数量
            break