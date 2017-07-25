#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import json
import traceback

import requests

from Config import checkUpdateBaseUrl
from app.QuanBenMianFeiCrawler import handlChapByBookObjChapObj
from app.baseCrawler import BaseCrawler

from dao.dushuQuanBenService import getQuanBenAllLianZaiBookObjs
from dao.dushuService import updateOneFieldByOneField, updateBoostWithUpdateTime, getBookObjById, \
    getLatestChapByBookId, getChapTitlesByBookId, getCapIdxsByBookId
from exception.InputException import InputException
from util.logHelper import myLogging


def updateFromMysql():
    '''
        永远运行，从数据库中查询出于连载状态的小说，进行更新
    '''

    bookObjs = getQuanBenAllLianZaiBookObjs()
    for bookObj in bookObjs:
        try:
            updateByBookObj(bookObj)
        except Exception as e:
            myLogging.error('update book' + str(bookObj['id']) + ' raise exception ')
            myLogging.error(traceback.format_exc())


def updateByDbBookId(dbid):
    bookObj = getBookObjById(dbid)
    if not bookObj:
        raise InputException('wrong id')
    updateByBookObj(bookObj)


def updateByBookObj(bookObj):
    latestChapObj = getLatestChapByBookId(bookObj['id'])

    chapName = ''
    chapIdx = 0
    if latestChapObj:
        chapName = latestChapObj['title']
        chapIdx = latestChapObj['idx']

    source = bookObj['source']

    checkUpdateUrl = checkUpdateBaseUrl % source

    payload = {
        'client_chapter_name': chapName.encode('utf-8'),
        'client_bookmark_name': chapName.encode('utf-8'),
        'client_chapter_count': int(chapIdx),
        'client_bookmark_count': int(chapIdx)
    }

    headers = {
        u'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1; M3s Build/LMY47I)',
        u'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    r = requests.post(checkUpdateUrl, data=payload, headers=headers)

    resp = r.text

    respJson = json.loads(resp)
    if not respJson['items'] or len(respJson['items']) < 1 or respJson['total'] < 1:
        myLogging.info('%s no update, skip', bookObj['id'])
        return
    resIdx = chapIdx
    chapTitles = getChapTitlesByBookId(bookObj['id'])
    chapIdxs = getCapIdxsByBookId(bookObj['id'])
    for chapObj in respJson['items']:
        # if chapObj['serial_number'] <= chapIdx:
        tempIdx = chapObj['serial_number']
        tempTitle = chapObj['name']
        if chapObj['serial_number'] <= chapIdx and tempIdx in chapIdxs and tempTitle in chapTitles:
            continue
        try:
            chapIdx = handlChapByBookObjChapObj(chapObj=chapObj, bookObj=bookObj, allowUpdate=True)
            resIdx = max(resIdx, chapIdx)
        except Exception as e:
            myLogging.error('bookId %s chap idx %s has exception: %s', bookObj['id'], chapObj['serial_number'],
                            traceback.format_exc())

    if resIdx > bookObj['chapterNum']:
        updateOneFieldByOneField('chapterNum', resIdx, 'id', bookObj['id'])

        updateBoostWithUpdateTime(bookObj['id'])

        myLogging.info(str(bookObj['id']) + respJson['book']['name'].encode('utf-8') + ' update ' + str(
            resIdx - bookObj['chapterNum']) \
                       + ' chaps ')

        if u'serialize' == respJson['book']['status']:
            newStatus = u'连载'
            if u'FINISH' == respJson['book']['status']:
                newStatus = u'完结'
            updateOneFieldByOneField('bookType', newStatus, 'id', bookObj['id'])
            myLogging.warning(bookObj['title'].encode('utf-8') + newStatus.encode('utf-8'))
    else:
        myLogging.info(str(bookObj['id']) + ' has unexcepted, please check. didnot update ')


class QuanBenUpdater(BaseCrawler):
    def __init__(self):
        self.bookId = None

    def init(self, data=None):
        if data and isinstance(data, dict) and data.has_key('bookId'):
            self.bookId = data['bookId']

    def crawl(self):
        if self.bookId:
            updateByDbBookId(self.bookId)
        else:
            updateFromMysql()

    def output(self):
        pass


if __name__ == '__main__':
    # fixUnFinished()
    # updateFromMysql()
    updateByDbBookId(2137876)
