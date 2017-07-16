#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import json
import traceback


from app.ZhuiShuShenQiCrawler import getChapsByBocId, handlChapsByBookObjZidBocId
from app.baseCrawler import BaseCrawler

from dao.dushuService import updateOneFieldByOneField, updateBoostWithUpdateTime, getBookObjById

from dao.dushuZssqService import getZssqAllLianZaiBookObjs
from exception.InputException import InputException
from util.logHelper import myLogging


def updateFromMysql():
    '''
        永远运行，从数据库中查询出于连载状态的小说，进行更新
    '''

    bookObjs = getZssqAllLianZaiBookObjs()
    for bookObj in bookObjs:
        try:
            updateByBookObj(bookObj)
        except Exception as e:
            myLogging.error('update book' + str(bookObj['id']) +' raise exception ')
            myLogging.error(traceback.format_exc())

def updateByDbBookId(dbid):

    bookObj = getBookObjById(dbid)
    if not bookObj:
        raise InputException('wrong id')
    updateByBookObj(bookObj)

def updateByBookObj(bookObj):
    source = bookObj['source']
    [zid, zBocId] = source.split('/')
    currentChapsObj = getChapsByBocId(zBocId)
    if not currentChapsObj or not currentChapsObj.has_key('chapters') or len(currentChapsObj['chapters']) < 1:
        # delBookById(bookObj['id'])
        myLogging.error( 'shuqi book has been droped, plz consider to delete id: '+ str(bookObj['id'])+ ' sid: '+ str(source))
        return
    currentChapNum = len(currentChapsObj['chapters'])
    if currentChapNum > bookObj['chapterNum']:

        newIdx = handlChapsByBookObjZidBocId(bookObj, zid, currentChapsObj, allowUpdate=True)

        if newIdx  > bookObj['chapterNum']:
            updateOneFieldByOneField('chapterNum', newIdx, 'id', bookObj['id'])
            updateBoostWithUpdateTime(bookObj['id'])
            myLogging.info('zid: %s, bookId: %s  update %s chaps ', zid, bookObj['id'], str(newIdx - bookObj['chapterNum']) )

    else:
        myLogging.info('zid: %s, bookId: %s no update ()', zid, bookObj['id'])


class ZssqUpdater(BaseCrawler):

    def __init__(self):
        self.bookId = None

    def init(self, data = None):
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
    updateFromMysql()
