##!/usr/bin/python
# -*- coding: UTF-8 -*-
from app.baseCrawler import BaseCrawler
from app.mianfeiTXTCrawler import crawlCurrentBookObj, handleCapsByBookObj
from dao.dushuMianFeiTXTService import getMianAllBookObjs
from dao.dushuService import updateOneFieldByOneField, getBookObjById, updateBoostWithUpdateTime
from exception import InputException


def mianfeiTxtUpdateFromMysql():
    bookObjs = getMianAllBookObjs()
    for bookObj in bookObjs:

        mianfeiUpdateByBookObj(bookObj)


def mianfeiUpdateByBookObj(bookObj):
    mid = bookObj['source']
    newBookObj, newChapNum = crawlCurrentBookObj(mid)
    if newChapNum > bookObj['chapterNum']:
        resIdx = handleCapsByBookObj(allowUpdate=True, bookObj=bookObj, count=newBookObj['chapterNum']
                                     , mid=mid, startCapIdx=bookObj['chapterNum'])
        if resIdx > bookObj['chapterNum']:
            updateOneFieldByOneField('chapterNum', resIdx, 'id', bookObj['id'])
            updateBoostWithUpdateTime(bookObj['id'])
            print newBookObj['title'].encode('utf-8') + ' update ' + str(resIdx - bookObj['chapterNum']) + ' chaps'
            if '连载' != newBookObj['bookType']:
                updateOneFieldByOneField('bookType', newBookObj['bookType'], 'id', bookObj['id'])
                print newBookObj['title'].encode('utf-8') + newBookObj['bookType']
    else:
        print newBookObj['title'].encode('utf-8') + ' no update'

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