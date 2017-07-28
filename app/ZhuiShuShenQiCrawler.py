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

from Config import ZSSQBOOKINFOBASEURL, ZSSQCHAPCONTENTBASEURL, MINCHAPNUM, sourceLimit, MinChapContentLength
from app.baseCrawler import BaseCrawler
# from app.shuqi import shuqCategory
from dao.aliyunOss import uploadJson2Bucket
from dao.dushuService import insertBookWithConn, insertCapWithCapObj, getChapTitlesByBookId, getCapIdxsByBookId, \
    delBookById
from exception.InputException import InputException
from parse.contentHelper import textClean
from util.UUIDUtils import getCapDigest
from util.categoryHelper import getClassifyCodeByName, getCategoryAndTypeCode
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA


def startByZid(zid, allowUpdate=False):

    bookObj = getBookObjBiZid(zid)
    if not bookObj:
        myLogging.error('zid %s get bookObj null', zid)
        return

    bookObj = parseBook(allowUpdate, bookObj, zid)


    # bocObjs = getBocObjsByZid(zid)

    # bookObj['source'] = zid + '/' + bocId
    # bookObj['rawUrl'] = ZSSQBOOKINFOBASEURL + str(zid)

    # bookObj = insertBookWithConn(bookObj, allowUpdate)
    if not bookObj:
        myLogging.error('zid %s parse and insert bookObj null', zid)
        return

    handleChapsByBookObj(bookObj, zid, allowUpdate)


def handleChapsByBookObj(bookObj, zid, allowUpdate = False):

    # zid = bookObj['source']

    bocObjs = getBocObjsByZid(zid)

    sourceCount = 0
    for bocIdx in range(0, len(bocObjs)):
        bocObj = bocObjs[bocIdx]
        bocId = bocObj['_id']

        try:

            bocSource = bocObj['source']
            if 'zhuishuvip' == bocSource:
                continue

            bookObj['source'] = zid + '/' + bocId
            bookObj['rawUrl'] = ZSSQBOOKINFOBASEURL + str(zid) + "?source=" + str(bocId)
            chapListObj = getChapsByBocId(bocId)
            bookObj['chapterNum'] = min(bookObj['chapterNum'], len(chapListObj['chapters']))

            if bookObj['chapterNum'] <= MINCHAPNUM:
                continue

            bookObj = insertBookWithConn(bookObj, allowUpdate)

            resInx = handlChapsByBookObjZidBocId(bookObj, zid, chapListObj,allowUpdate )
            if resInx <= MINCHAPNUM:
                myLogging.info('zid %s dbid %s crawl too small chapNum, delete ', zid, bookObj['id'])
                delBookById(bookObj['id'])

            sourceCount += 1
            if sourceCount >= sourceLimit:
                myLogging.info('zid: %s crawl source to sourceLimit', zid)
                break
            else:
                # bookObj['rawUrl'] = ZSSQBOOKINFOBASEURL + str(zid) + "?source=" + str(bocId)
                # bookObj = parseInsertBook(allowUpdate, bookObj, zid) #重新插入另外一个源的书
                myLogging.info('zid: %s crawl another source %s', zid, bocId)
        except Exception as e:
            myLogging.error('zid: %s ,bocId %s get exception ', zid,bocId)
            myLogging.error(traceback.format_exc())


def handlChapsByBookObjZidBocId(bookObj, zid,chapListObj, allowUpdate= False):
    # chapListObj = getChapsByBocId(bocId)
    resInx = 0 #保存最终更新到的下标
    # chapListObj = getChapObjs(bookObj)
    if not chapListObj:
        myLogging.error('zid %s get chaps list null', zid)
        return resInx
    if not chapListObj.has_key('chapters'):
        myLogging.error('zid %s chaps list no data', zid)
        return resInx
    capIdxs = set()
    capTitles = set()
    if allowUpdate:
        capIdxs = getCapIdxsByBookId(bookObj['id'])  # 已在库中的章节下标
        capTitles = getChapTitlesByBookId(bookObj['id'])  # 已在库中的章节下标
    for idx in range(0, len(chapListObj['chapters'])):
        try:
            # if idx in capIdxs:
            #     continue

            chapObj = chapListObj['chapters'][idx]

            if chapObj['title'] in capTitles:
                continue
            if idx in capIdxs:
                continue
            chapObj['cid'] = chapObj['link']
            if chapObj.has_key('id'):
                chapObj['cid'] = chapObj['id']
            chapObj['idx'] = idx

            chapContentUrl = ZSSQCHAPCONTENTBASEURL + quote(chapObj['link'])
            chapContentText = getContentWithUA(chapContentUrl)
            if not chapContentText:
                myLogging.error('zid: %s, dbid: %s, chapId: %s, get chapContent null ', zid, bookObj['id'],
                                chapObj['cid'])
                continue
            chapContentObj = json.loads(chapContentText)
            if not chapContentObj or not chapContentObj.has_key('chapter'):
                myLogging.error('zid: %5, dbid: %s, chapId: %s, get no chapter ', zid, bookObj['id'],
                                chapObj['cid'])
                continue
            if u'.' == chapContentObj['chapter']['title'] or len(chapContentObj['chapter']['title']) < 2:
                del chapContentObj['chapter']['title']
            chapObj.update(chapContentObj['chapter'])

            chapObj['content'] = chapObj['body']
            if chapObj.has_key('cpContent'):
                chapObj['content'] = chapObj['cpContent']
                del chapObj['cpContent']
            chapObj['content'] = textClean(chapObj['content'])

            if len(chapObj['content']) < MinChapContentLength:
                myLogging.error('zid %s cid %s content too small skip', zid,chapObj['cid'])
                continue

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
            uploadJson2Bucket(str(capId) + '.json', json.dumps(chapObj))

            resInx = max(resInx, idx)
            # aftUploadCap = time.time()
            # uploadCap = uploadCap + (aftUploadCap - aftInsertCap)
        except Exception as e:
            myLogging.error('zid: %, dbid: %s, idx: %s, get exception ', zid, bookObj['id'],
                            idx)
            myLogging.error(traceback.format_exc())
    return resInx

# def getChapObjs(bookObj):
#     zid = bookObj['zid']
#
#     bocObjs = getBocObjsByZid(zid)
#     for bocIdx in range(0, len(bocObjs)):
#         bocObj = bocObjs[bocIdx]
#         bocId = bocObj['_id']
#         chapListObj = getChapsByBocId(bocId)
#     return chapListObj


def getBocObjsByZid(zid):
    getbocBaseUrl = 'http://api.zhuishushenqi.com/atoc?view=summary&book='
    botText = getContentWithUA(getbocBaseUrl + zid)
    bocObjs = json.loads(botText)
    return bocObjs


# def getChapsByBocId(bocIdx, bocObjs):
def getChapsByBocId(bocId):
    chapListUrl = 'http://api.zhuishushenqi.com/btoc/%s?view=chapters' % (bocId)
    chapsText = getContentWithUA(chapListUrl)
    # if not chapsText:
    # return
    chapListObj = json.loads(chapsText)
    return chapListObj


def parseBook(allowUpdate, bookObj, zid):

    # categDict = shuqCategory
    zssqStaticUrl = 'http://statics.zhuishushenqi.com/'

    bookObj['zid'] = bookObj['_id']

    bookObj['imgUrl'] = urlparse.urljoin(zssqStaticUrl, bookObj['cover'])
    bookObj['category'] = '其他'
    if bookObj.has_key('majorCate'):
        bookObj['category'] = bookObj['majorCate']

    # bookObj['categoryCode'] = getClassifyCodeByName(bookObj['category'])['categoryCode']

    bookObj['type'] = '其他'
    if bookObj.has_key('minorCate'):
        bookObj['type'] = bookObj['minorCate']
    # bookObj['type'] = bookObj['minorCate']
    bookObj['typeCode'] = 0
    # classfyObj = getClassifyCodeByName(bookObj['type'])
    # if 0 != classfyObj['typeCode']:#二级分类命中的话 一级分类也可以更新掉了
    #     bookObj['typeCode'] = classfyObj['typeCode']
    #     bookObj['categoryCode'] = classfyObj['categoryCode']

    bookObj['categoryCode'], bookObj['typeCode'], bookObj['category'] = getCategoryAndTypeCode(bookObj['category'], bookObj['type'])


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