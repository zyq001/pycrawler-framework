#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书神器
@author: zyq
'''
import json
import traceback
import urlparse
from urllib import quote

import time

from Config import ZSSQBOOKINFOBASEURL, ZSSQCHAPCONTENTBASEURL, MINCHAPNUM
from app.baseCrawler import BaseCrawler
from app.shuqi import shuqCategory
from dao.aliyunOss import upload2Bucket
from dao.dushuService import insertBookWithConn, insertCapWithCapObj, getCapIdxsByBookId
from exception.InputException import InputException
from util.UUIDUtils import getCapDigest
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA


def startByZid(zid, allowUpdate=False):

    bookObj = getBookObjBiZid(zid)
    if not bookObj:
        myLogging.error('zid %s get bookObj null', zid)
        return

    bookObj = parseInsertBook(allowUpdate, bookObj, zid)
    if not bookObj:
        myLogging.error('zid %s parse and insert bookObj null', zid)
        return

    handleChapsByBookObj(bookObj, allowUpdate)


def handleChapsByBookObj(bookObj, allowUpdate = False):

    zid = bookObj['source']

    bocObjs = getBocObjsByZid(zid)

    for bocIdx in range(0, len(bocObjs)):
        chapListObj = getChapsByBocId(bocIdx, bocObjs)

    # chapListObj = getChapObjs(bookObj)
        if not chapListObj:
            myLogging.error('zid %s get chaps list null', zid)
            return
        if not chapListObj.has_key('chapters'):
            myLogging.error('zid %s chaps list no data', zid)
            return


        capIdxs = set()
        if allowUpdate:
            capIdxs = getCapIdxsByBookId(bookObj['id'])  # 已在库中的章节下标

        for idx in range(0, len(chapListObj['chapters'])):
            try:
                chapObj = chapListObj['chapters'][idx]
                chapObj['cid'] = chapObj['id']
                chapObj['idx'] = idx

                chapContentUrl = ZSSQCHAPCONTENTBASEURL + quote(chapObj['link'])
                chapContentText = getContentWithUA(chapContentUrl)
                if not chapContentText:
                    myLogging.error('zid: %, dbid: %s, chapId: %s, get chapContent null ', bookObj['zid'], bookObj['id'],
                                    chapObj['cid'])
                    continue
                chapContentObj = json.loads(chapContentText)
                if not chapContentObj or not chapContentObj.has_key('chapter'):
                    myLogging.error('zid: %, dbid: %s, chapId: %s, get no chapter ', bookObj['zid'], bookObj['id'],
                                    chapObj['cid'])
                    continue
                chapObj.update(chapContentObj['chapter'])

                chapObj['content'] = chapObj['cpContent']
                del chapObj['cpContent']
                del chapObj['body']
                del chapObj['link']
                chapObj['rawUrl'] = chapContentUrl
                # capObj['size'] = int(WordsCount)
                chapObj['size'] = len(chapObj['content'])
                chapObj['bookId'] = bookObj['id']
                chapObj['source'] = bookObj['source']
                chapObj['bookUUID'] = bookObj['digest']

                digest = getCapDigest(bookObj, chapObj, chapObj['cid'])
                chapObj['digest'] = digest

                capId = insertCapWithCapObj(chapObj)

                # aftInsertCap = time.time()
                # insertCap = insertCap + (aftInsertCap - befInsertCap)

                if not capId:
                    continue
                upload2Bucket(str(chapObj['id']) + '.json', json.dumps(chapObj))

                # aftUploadCap = time.time()
                # uploadCap = uploadCap + (aftUploadCap - aftInsertCap)
            except Exception as e:
                myLogging.error('zid: %, dbid: %s, idx: %s, get exception ', bookObj['zid'], bookObj['id'],
                                idx)
                myLogging.error(traceback.format_exc())


def getChapObjs(bookObj):
    zid = bookObj['zid']

    bocObjs = getBocObjsByZid(zid)
    for bocIdx in range(0, len(bocObjs)):
        chapListObj = getChapsByBocId(bocIdx, bocObjs)
    return chapListObj


def getBocObjsByZid(zid):
    getbocBaseUrl = 'http://api.zhuishushenqi.com/atoc?view=summary&book='
    botText = getContentWithUA(getbocBaseUrl + zid)
    bocObjs = json.loads(botText)
    return bocObjs


def getChapsByBocId(bocIdx, bocObjs):
    bocObj = bocObjs[bocIdx]
    bocId = bocObj['_id']
    chapListUrl = 'http://api.zhuishushenqi.com/btoc/%s?view=chapters' % (bocId)
    chapsText = getContentWithUA(chapListUrl)
    # if not chapsText:
    # return
    chapListObj = json.loads(chapsText)
    return chapListObj


def parseInsertBook(allowUpdate, bookObj, zid):

    categDict = shuqCategory
    zssqStaticUrl = 'http://statics.zhuishushenqi.com/'

    bookObj['zid'] = bookObj['_id']

    bookObj['imgUrl'] = urlparse.urljoin(zssqStaticUrl, bookObj['cover'])
    bookObj['category'] = bookObj['majorCate']
    bookObj['type'] = bookObj['minorCate']
    bookObj['typeCode'] = 0
    if categDict.has_key(bookObj['type']):
        if categDict[bookObj['type']]['id'] and len(categDict[bookObj['type']]['id']) > 0:
            bookObj['typeCode'] = int(categDict[bookObj['type']]['id'])
    bookObj['category'] = bookObj['majorCate']
    bookObj['categoryCode'] = 0
    if categDict.has_key(bookObj['category']):
        if categDict[bookObj['category']]['id'] and len(categDict[bookObj['category']]['id']) > 0:
            bookObj['categoryCode'] = int(categDict[bookObj['category']]['id'])
    bookObj['size'] = bookObj['wordCount']
    bookObj['chapterNum'] = bookObj['chaptersCount']


    if bookObj['chapterNum'] < MINCHAPNUM:
        myLogging.warning( 'chapNum too small, skip %s,  return', str(zid))
        return None

    bookObj['subtitle'] = bookObj['longIntro']
    bookObj['viewNum'] = int(bookObj['latelyFollower']) * 9
    if bookObj['isSerial']:
        bookObj['bookType'] = '连载'
    else:
        bookObj['bookType'] = '完结'
    bookObj['source'] = zid
    bookObj['rawUrl'] = ZSSQBOOKINFOBASEURL + str(zid)

    bookObj = insertBookWithConn(bookObj, allowUpdate)
    return bookObj



def getBookObjBiZid(zid):

    bookInfoUrl = ZSSQBOOKINFOBASEURL + str(zid)
    bookInfoText = getContentWithUA(bookInfoUrl)
    if not bookInfoText:
        return None
    return json.loads(bookInfoText)


class ZssqCrawler(BaseCrawler):

    def __init__(self, zid = None):
        self.zid = zid

    def init(self, data = None):
        print 'zssq init'

        if not data or not isinstance(data, dict):
            raise InputException("requried dict data with fields: sid")
        if not data.has_key('id'):
            raise InputException("requried field 'id' in data")

        self.zid = data['id']

    def crawl(self, allowUpdate = False):
        print 'zssq crawl'
        if self.zid:
            startByZid(self.zid, allowUpdate)

    def output(self):
        print 'zssq output'

    def search(self, input):
        print 'zssq search '

if __name__ == '__main__':
    ZssqCrawler('56928442c49f3bce42b7f521').crawl()