##!/usr/bin/python
# -*- coding: UTF-8 -*-
import traceback

from app.baseCrawler import BaseCrawler
from app.mianfeiTXTCrawler import crawlCurrentBookObj, handleCapsByBookObj
from dao.dushuMianFeiTXTService import getMianAllBookObjs
from dao.dushuService import updateOneFieldByOneField, getBookObjById, updateBoostWithUpdateTime
from exception import InputException
from util.logHelper import myLogging


def mianfeiTxtUpdateFromMysql():
    bookObjs = getMianAllBookObjs()
    for bookObj in bookObjs:
        try:
            mianfeiUpdateByBookObj(bookObj)

        except Exception as e:
            myLogging.error('mianTxt update book' + str(bookObj['id']) +' raise exception ')
            myLogging.error(traceback.format_exc())

def mianfeiUpdateByBookObj(bookObj):
    mid = bookObj['source']
    newBookObj, newChapNum = crawlCurrentBookObj(mid)
    latestCapIndex = newBookObj['latestCapIndex']
    newChapNum = max(newChapNum, latestCapIndex)
    if newChapNum > bookObj['chapterNum'] :
        resIdx = handleCapsByBookObj(allowUpdate=True, bookObj=bookObj, count=newChapNum
                                     , mid=mid, startCapIdx=bookObj['chapterNum'])
        if resIdx > bookObj['chapterNum']:
            updateOneFieldByOneField('chapterNum', resIdx, 'id', bookObj['id'])
            updateBoostWithUpdateTime(bookObj['id'])
            myLogging.info( newBookObj['title'].encode('utf-8') + ' update ' \
                  + str(resIdx - bookObj['chapterNum']) + ' chaps (mianTxt) ')
            if '连载' != newBookObj['bookType']:
                updateOneFieldByOneField('bookType', newBookObj['bookType'], 'id', bookObj['id'])
                myLogging.info( newBookObj['title'].encode('utf-8') + newBookObj['bookType'])
    else:
        myLogging.debug(newBookObj['title'].encode('utf-8') + ' no update (mianTxt)')

def mianfeiUpdateById(dbid):
    '''
    按照我们库里主键id更新，可以用于客户端用户出发更新
    :param dbid: 
    :return: 
    '''
    bookObj = getBookObjById(dbid)
    if not bookObj:
        raise InputException('wrong id')

    mianfeiUpdateByBookObj(bookObj)

class MianFeiTXTUpdater(BaseCrawler):

    def __init__(self):
        self.bookId = None

    def init(self, data = None):
        if data and isinstance(data, dict) and data.has_key('bookId'):
            self.bookId = data['bookId']

    def crawl(self):
        if self.bookId:
            mianfeiUpdateById(self.bookId)
        else:
            mianfeiTxtUpdateFromMysql()
    def output(self):
        pass


if __name__ == '__main__':
    mianfeiTxtUpdateFromMysql()
    # mianfeiUpdateById(2010194)