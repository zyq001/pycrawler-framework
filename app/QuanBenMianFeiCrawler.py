#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书神器
@author: zyq
'''
import json
import random
import traceback
import urlparse
from urllib import quote

import time

from Config import ZSSQBOOKINFOBASEURL, ZSSQCHAPCONTENTBASEURL, MINCHAPNUM, bookInfoBaseUrl, \
    srcListBaseUrl, chapListBaseUrl, MinChapContentLength
from app.baseCrawler import BaseCrawler
# from app.shuqi import shuqCategory
from dao.aliyunOss import upload2Bucket, uploadJson2Bucket
from dao.dushuService import insertBookWithConn, insertCapWithCapObj, getCapIdxsByBookId
from exception.InputException import InputException
from util.UUIDUtils import getCapDigest
from util.categoryHelper import getClassifyCodeByName
from util.contentHelper import textClean
from util.defaultImgHelper import checkDefaultImg
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA


def startByQid(zid, srcId = None, allowUpdate=False):



    bookObj = getBookObjBiQid(zid, srcId, allowUpdate)
    # if not bookObj:
    #     myLogging.error('zid %s get bookObj null', zid)
    #     return
    #
    # bookObj = parseInsertBook(allowUpdate, bookObj, zid)
    # if not bookObj:
    #     myLogging.error('zid %s parse and insert bookObj null', zid)
    #     return
    #
    # handleChapsByBookObj(bookObj, allowUpdate)


# def handleChapsByBookObj(bookObj, allowUpdate = False):
#
#     zid = bookObj['source']
#
#     bocObjs = getBocObjsByZid(zid)
#
#     for bocIdx in range(0, len(bocObjs)):
#         chapListObj = getChapsByBocId(bocIdx, bocObjs)
#
#     # chapListObj = getChapObjs(bookObj)
#         if not chapListObj:
#             myLogging.error('zid %s get chaps list null', zid)
#             return
#         if not chapListObj.has_key('chapters'):
#             myLogging.error('zid %s chaps list no data', zid)
#             return
#
#
#         capIdxs = set()
#         if allowUpdate:
#             capIdxs = getCapIdxsByBookId(bookObj['id'])  # 已在库中的章节下标
#
#         for idx in range(0, len(chapListObj['chapters'])):
#             try:
#                 chapObj = chapListObj['chapters'][idx]
#                 chapObj['cid'] = chapObj['id']
#                 chapObj['idx'] = idx
#
#                 chapContentUrl = ZSSQCHAPCONTENTBASEURL + quote(chapObj['link'])
#                 chapContentText = getContentWithUA(chapContentUrl)
#                 if not chapContentText:
#                     myLogging.error('zid: %, dbid: %s, chapId: %s, get chapContent null ', bookObj['zid'], bookObj['id'],
#                                     chapObj['cid'])
#                     continue
#                 chapContentObj = json.loads(chapContentText)
#                 if not chapContentObj or not chapContentObj.has_key('chapter'):
#                     myLogging.error('zid: %, dbid: %s, chapId: %s, get no chapter ', bookObj['zid'], bookObj['id'],
#                                     chapObj['cid'])
#                     continue
#                 chapObj.update(chapContentObj['chapter'])
#
#                 chapObj['content'] = chapObj['cpContent']
#                 del chapObj['cpContent']
#                 del chapObj['body']
#                 del chapObj['link']
#                 chapObj['rawUrl'] = chapContentUrl
#                 # capObj['size'] = int(WordsCount)
#                 chapObj['size'] = len(chapObj['content'])
#                 chapObj['bookId'] = bookObj['id']
#                 chapObj['source'] = bookObj['source']
#                 chapObj['bookUUID'] = bookObj['digest']
#
#
#                 digest = getCapDigest(bookObj, chapObj, chapObj['cid'])
#                 chapObj['digest'] = digest
#
#                 capId = insertCapWithCapObj(chapObj)
#
#                 # aftInsertCap = time.time()
#                 # insertCap = insertCap + (aftInsertCap - befInsertCap)
#
#                 if not capId:
#                     continue
#                 upload2Bucket(str(chapObj['id']) + '.json', json.dumps(chapObj))
#
#                 # aftUploadCap = time.time()
#                 # uploadCap = uploadCap + (aftUploadCap - aftInsertCap)
#             except Exception as e:
#                 myLogging.error('zid: %, dbid: %s, idx: %s, get exception ', bookObj['zid'], bookObj['id'],
#                                 idx)
#                 myLogging.error(traceback.format_exc())


def getSourceId(qid):
    srcUrl = srcListBaseUrl % str(qid)

    srcListContent = getContentWithUA(srcUrl)
    if not srcListContent:
        return
    srcJsonObj = json.loads(srcListContent)
    if not srcJsonObj or not srcJsonObj.has_key('items'):
        myLogging.error('no  srcObj items qid %s', qid)
        return

    srcItems = srcJsonObj['items']

    if len(srcItems.keys()) < 1:
        myLogging.error('  srcObj items len < 1 qid %s', qid)
        return

    if srcItems.has_key('api.zhuishuwang.com'):
        return srcItems['api.zhuishuwang.com'][0]['book_source_id']

    # updateTIme = 0
    # resId = ''
    # for itmkey in srcItems.keys():
    #     if srcItems[itmkey][0]['update_time'] > updateTIme:
    #         resId = srcItems[itmkey][0]['book_source_id']
    #         updateTIme = srcItems[itmkey][0]['update_time']
    #
    # return resId
    raise InputException('no zhuishuwang source, skip')


def getBookObjBiQid(qid, srcId = None, allowUpdate=False):
    if not srcId:
        srcId = getSourceId(qid)

    # categDict = shuqCategory

    bookInfoUrl = bookInfoBaseUrl % (qid, srcId)
    bookInfoContent = getContentWithUA(bookInfoUrl)
    bookInfoObj = json.loads(bookInfoContent)
    bookObj = bookInfoObj['items'][0]
    bookObj['title'] = bookObj['name']
    bookObj['subtitle'] = bookObj['desc']
    bookObj['imgUrl'] = checkDefaultImg(bookObj['img_url'])

    if bookObj['status'] == 'SERIALIZE':
        bookObj['bookType'] = u'连载'
    else:
        bookObj['bookType'] = u'完结'

    bookObj['rawUrl'] = bookInfoUrl

    bookObj['category'] = bookObj['labels']
    bookObj['categoryCode'] = getClassifyCodeByName(bookObj['category'])['categoryCode']

    # if categDict.has_key(bookObj['category']):
    #     if categDict[bookObj['category']]['id'] and len(categDict[bookObj['category']]['id']) > 0:
    #         bookObj['categoryCode'] = int(categDict[bookObj['category']]['id'])

    bookObj['type'] = bookObj['category']
    bookObj['typeCode'] = 0
    classObj = getClassifyCodeByName(bookObj['type'])
    if 0 != classObj['typeCode']:
        bookObj['typeCode'] = classObj['typeCode']
        bookObj['categoryCode'] = classObj['categoryCode']

    bookObj['source'] = qid + '/' + srcId

    chapListUrl = chapListBaseUrl % (qid, srcId)

    chapListContent = getContentWithUA(chapListUrl)

    chapListObj = json.loads(chapListContent)

    chapNum = len(chapListObj['items'])
    bookObj['chapterNum'] = chapNum

    if bookObj['chapterNum'] < MINCHAPNUM:
        myLogging.error('chap num too small skip, bookId %s', qid)
        return
    bookObj['size'] = chapNum * random.randint(1000, 3000)
    bookObj['viewNum'] = chapNum * random.randint(20000, 30000)

    bookObj = insertBookWithConn(bookObj, allowUpdate)

    if not bookObj:
        myLogging.error('null bookObj after insert Book to db, bookId %s', qid)
        return

    for chapObj in chapListObj['items']:

        try:
            handlChapByBookObjChapObj(allowUpdate, bookObj, chapObj)

        except Exception as e:
            myLogging.error(traceback.format_exc())

    # return bocObjs


def handlChapByBookObjChapObj(allowUpdate, bookObj, chapObj):
    chapContentUrl = chapObj['url']
    chapContent = getContentWithUA(chapContentUrl)
    chapContentObj = json.loads(chapContent)
    if not chapContentObj or not chapContentObj['content'] or len(chapContentObj['content']) < MinChapContentLength:
        myLogging.error('zid %s content too small skip, chapContentUrl %s', bookObj['id'], chapContentUrl)
        return 0

    chapObj.update(chapContentObj)
    chapObj['title'] = chapObj['name']
    chapObj['rawUrl'] = chapContentUrl
    chapObj['idx'] = int(chapObj['serialNumber'])
    del chapObj['serialNumber']
    chapObj['size'] = len(chapObj['content'])
    chapObj['bookId'] = bookObj['id']
    chapObj['source'] = bookObj['source']
    chapObj['bookUUID'] = bookObj['digest']
    digest = getCapDigest(bookObj, chapObj, chapObj['bookChapterId'])
    chapObj['digest'] = digest
    chapObj['content'] = textClean(chapObj['content'])
    capId = insertCapWithCapObj(chapObj, allowUpdate=allowUpdate)
    # aftInsertCap = time.time()
    # insertCap = insertCap + (aftInsertCap - befInsertCap)
    if not capId:
        myLogging.error('no chapId cid %s', chapObj['bookChapterId'])
        return 0
    uploadJson2Bucket(str(chapObj['id']) + '.json', json.dumps(chapObj))

    return chapObj['idx']

class QuanBenCrawler(BaseCrawler):

    def __init__(self, zid = None):
        self.qid = zid

    def init(self, data = None):
        print 'quanben init'

        if not data or not isinstance(data, dict):
            raise InputException("requried dict data with fields: sid")
        if not data.has_key('id'):
            raise InputException("requried field 'id' in data")

        self.qid = data['id']

    def crawl(self, allowUpdate = False):
        print 'quanben crawl'
        if self.qid:
            print 'bookId : ' + self.qid
            startByQid(self.qid, allowUpdate=allowUpdate)

    def output(self):
        print 'quanben output'

    def search(self, input):
        print 'quanben search '

# if __name__ == '__main__':
    # ZssqCrawler('56928442c49f3bce42b7f521').crawl()
    # QuanBenCrawler('576908fad48745522ce1fbd7').crawl()