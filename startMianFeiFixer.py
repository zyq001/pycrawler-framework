#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import json
from urllib import quote

import requests

from Config import MianFeiTXTSearchBaseUrl, MianFeiTXTChapBaseUrl
from app.mianFeiFixer import fixUnFinished
from dao.dushuMianFeiTXTService import getMianAllBookObjs, getMianAllBookBaseObjs
from dao.dushuService import getLatestChapByBookId, updateOneFieldByOneField
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA
from util.signHelper import paramMap


def changeSouceIds():
    bookObjs = getMianAllBookBaseObjs()
    for bookObj in bookObjs:
        title = bookObj['title']
        author = bookObj['author']
        source = bookObj['source']
        bookId = bookObj['id']

        searchUrl = MianFeiTXTSearchBaseUrl + '?' + paramMap().mianfeiTXT()\
            .put('keyword', (title + author).encode('utf-8'))\
            .put('pageSize', '5').put('pageNum', '1').put('type', '1')\
            .mianfeiTXTSign() \
            .put('keyword', quote((title + author).encode('utf-8')))\
            .toUrl()

        r = requests.get(searchUrl)

        searchRes = json.loads(r.text)
        for resBook in searchRes['data']['books']:
            resTitle = resBook['name']
            if resTitle != title:
                continue
            resAuthor = resBook['author']
            if resAuthor != author:
                continue

            resId = resBook['bookId']

            latestChapObj = getLatestChapByBookId(bookId)
            if not latestChapObj:
                myLogging.error('no chaps in db yet, bookId: %s, new mid: %s', bookId, resId)
                # updateOneFieldByOneField('source', resId, 'id', bookId)
                break

            cid = latestChapObj['idx']
            chapTitle = latestChapObj['title']

            capContentUrl = MianFeiTXTChapBaseUrl + '?' + paramMap().mianfeiTXT().mBookId(resId).mChapId(
                cid).mianfeiTXTSign().toUrl()

            capContent = getContentWithUA(capContentUrl)
            if not capContent:
                capContent = getContentWithUA(capContentUrl)
            # capContent = capContent.replace(r'\r', '').replace(r'\n', '')
            capListJsonObj = json.loads(capContent, strict=False)
            if not (capListJsonObj['returnCode'] == '0000'):
                capListJsonObj = json.loads(capContent)
                if not (capListJsonObj['returnCode'] == '0000' and capListJsonObj['returnMsg'] == u'成功'):
                    myLogging.error('get chap detail fail mid: %s, cid: %s', resId, cid)
                    continue

            chapterName = capListJsonObj['data']['bookChapter']['chapterName']
            if chapterName == chapTitle:
                myLogging.info('bookId %s change source  from %s to %s', bookId, source, resId)
                # updateOneFieldByOneField('source', resId, 'id', bookId)

        myLogging.error('bookId %s did not find new id !!!,title: %s, author: %s, org source: %s', bookId, title, author,source )






if __name__ == '__main__':
    # fixUnFinished()

    # searchUrl = MianFeiTXTSearchBaseUrl + '?' + paramMap().mianfeiTXT() \
    #     .put('keyword', (u'大主宰').encode('utf-8')) \
    #     .put('pageSize', '10').put('pageNum', '1').put('type', '1') \
    #     .mianfeiTXTSign().toUrl()
    #
    # r = requests.get(searchUrl)
    #
    # searchRes = json.loads(r.text)
    changeSouceIds()